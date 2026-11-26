"""Bounded offline reference oracles; not canonical or legal authority."""

from __future__ import annotations

import re
import unicodedata
from collections import deque
from itertools import combinations

from .source_xml import parse_xml


def _grams(text: str, n: int) -> set[tuple[str, ...]]:
    words = re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def leakage(references: dict, outputs: dict, *, n: int = 8) -> dict:
    """Compare exact normalized word n-grams, returning no matching text.

    Output fragments must be supplied in extraction order. A clear result is only
    within these inputs and this normalization; missing coverage is a release hold.
    """
    if type(n) is not int or not 1 <= n <= 64:
        raise ValueError("invalid n-gram size")
    if not references or not outputs:
        return {"status": "held_incomplete", "matches": []}
    if any(not re.fullmatch(r"[A-Za-z0-9._/-]{1,128}", k) for k in (*references, *outputs)):
        raise ValueError("use opaque identifiers, not source text")
    if any(not isinstance(t, str) for t in references.values()) or any(
        not isinstance(parts, (list, tuple)) or any(not isinstance(p, str) for p in parts)
        for parts in outputs.values()
    ):
        raise ValueError("invalid extracted text")
    size = sum(map(len, references.values()))
    size += sum(len(p) for ps in outputs.values() for p in ps)
    if size > 1_000_000 or len(references) * len(outputs) > 10_000:
        return {"status": "held_limit", "matches": []}
    left = {k: _grams(v, n) for k, v in references.items()}
    right = {k: _grams(" ".join(v), n) for k, v in outputs.items()}
    matches = [
        (a, b, len(common))
        for a, x in sorted(left.items())
        for b, y in sorted(right.items())
        if (common := x & y)
    ]
    if matches:
        status = "held_match"
    elif not all(left.values()) or not all(right.values()):
        status = "held_incomplete"
    else:
        status = "clear_in_scope"
    return {"status": status, "matches": matches}


def applicability(rules: dict, facts: dict) -> dict:
    """Conjunctions of explicit boolean facts; missing is unknown, never false.

    A leading ! means an explicit negative literal; conflict takes precedence.
    The rule author supplies the complete applicability predicate.
    """
    if any(
        v is not True and v is not False and v is not None and v != "conflict"
        for v in facts.values()
    ):
        raise ValueError("invalid fact state")
    result = {}
    for requirement, predicates in sorted(rules.items()):
        if (
            not isinstance(predicates, (tuple, list))
            or not predicates
            or any(
                not isinstance(p, str) or not re.fullmatch(r"!?[A-Za-z0-9._-]+", p)
                for p in predicates
            )
        ):
            raise ValueError("invalid rule predicates")
        states = []
        for predicate in predicates:
            negative = predicate.startswith("!")
            value = facts.get(predicate.removeprefix("!"))
            states.append(not value if negative and type(value) is bool else value)
        if "conflict" in states:
            status = "held_conflict"
        elif False in states:
            status = "not_applicable"
        elif None in states:
            status = "unknown"
        else:
            status = "required"
        result[requirement] = status
    return result


def reachability(
    initial: tuple,
    final: tuple,
    transitions: dict,
    *,
    max_states: int = 1000,
    max_tokens: int = 100,
) -> dict:
    """Exhaust finite ordinary P/T marking graphs, holding on bound exhaustion.

    Soundness here means option to complete, proper completion and no dead
    transition in this finite graph. This is not a general PNML interpreter.
    """
    if (
        type(max_states) is not int
        or type(max_tokens) is not int
        or not 1 <= max_states <= 10_000
        or not 1 <= max_tokens <= 10_000
    ):
        raise ValueError("invalid reachability bounds")
    vectors = [initial, final, *(v for pair in transitions.values() for v in pair)]
    if (
        not initial
        or len(initial) > 256
        or len(transitions) > 256
        or any(
            len(v) != len(initial) or any(type(x) is not int or x < 0 for x in v)
            for v in vectors
        )
    ):
        raise ValueError("invalid marking or transition")
    held = {"status": "held_limit", "witness": [], "deadlocks": None}
    if max(sum(initial), sum(final)) > max_tokens:
        return held
    paths = {initial: []}
    queue = deque([initial])
    predecessors = {initial: set()}
    fired = set()
    deadlocks = 0
    proper = True
    while queue:
        state = queue.popleft()
        enabled = 0
        for name, (consume, produce) in sorted(transitions.items()):
            if any(x < y for x, y in zip(state, consume, strict=True)):
                continue
            enabled += 1
            fired.add(name)
            target = tuple(x - y + z for x, y, z in zip(state, consume, produce, strict=True))
            if sum(target) > max_tokens or (target not in paths and len(paths) == max_states):
                return held
            if target not in paths:
                paths[target] = [*paths[state], name]
                predecessors[target] = set()
                queue.append(target)
            predecessors[target].add(state)
        if state == final and enabled:
            proper = False
        if state != final and all(x >= y for x, y in zip(state, final, strict=True)):
            proper = False
        if state != final and not enabled:
            deadlocks += 1
    can_finish = {final} if final in paths else set()
    queue = deque(can_finish)
    while queue:
        for previous in predecessors[queue.popleft()] - can_finish:
            can_finish.add(previous)
            queue.append(previous)
    sound = proper and len(can_finish) == len(paths) and fired == set(transitions)
    return {
        "status": "sound_in_scope" if sound else "unsound",
        "witness": paths.get(final, []),
        "deadlocks": deadlocks,
        "states": len(paths),
        "dead_transitions": sorted(set(transitions) - fired),
    }


def alignment(edges: list, incompatible: list) -> dict:
    """Exact small maximum-weight equivalence subset with incompatible pairs.

    Only explicitly proposed equivalence edges enter this oracle. Topic and
    hierarchy edges are not equivalences. Hold ties; never delete obligations.
    """
    if len(edges) > 16:
        return {"status": "held_limit", "selected": [], "score": None}
    if any(a == b or type(w) is not int or w <= 0 for a, b, w in edges) or any(
        a == b for a, b in incompatible
    ):
        raise ValueError("invalid equivalence candidate or incompatibility")
    edges = sorted((min(a, b), max(a, b), w) for a, b, w in edges)
    if len({(a, b) for a, b, _ in edges}) != len(edges):
        raise ValueError("duplicate equivalence candidate")
    nodes = {x for a, b, _ in edges for x in (a, b)} | {
        x for a, b in incompatible for x in (a, b)
    }
    best = -1
    selected = []
    tied = False
    for count in range(len(edges) + 1):
        for subset in combinations(edges, count):
            score = sum(w for _, _, w in subset)
            if score < best:
                continue
            groups = {x: x for x in nodes}
            for a, b, _ in subset:
                left, right = groups[a], groups[b]
                groups = {x: left if g == right else g for x, g in groups.items()}
            if any(groups[a] == groups[b] for a, b in incompatible):
                continue
            if score == best:
                tied = True
            else:
                best, tied = score, False
                selected = [(a, b) for a, b, _ in subset]
    return {
        "status": "held_tie" if tied else "candidate_optimum",
        "selected": [] if tied else selected,
        "score": best,
    }


def rewrite(raw: bytes, edits: list) -> bytes:
    """Apply source-anchored byte edits; unchanged ranges are copied verbatim.

    Callers must obtain safe spans from a qualified parser and use an explicit
    normalization dictionary. This is not a CST or general-purpose transducer.
    """
    raw.decode("utf-8")
    if len(raw) > 1_000_000 or len(edits) > 1000:
        raise ValueError("rewrite limit exceeded")
    chunks = []
    position = 0
    for start, end, expected, replacement in sorted(edits):
        if not position <= start < end <= len(raw) or raw[start:end] != expected:
            raise ValueError("overlapping, invalid or stale edit")
        raw[position:start].decode("utf-8")
        expected.decode("utf-8")
        replacement.decode("utf-8")
        chunks.extend((raw[position:start], replacement))
        position = end
    chunks.append(raw[position:])
    return b"".join(chunks)


def verify_pnml(raw: bytes, *, max_states: int = 1000, max_tokens: int = 100) -> dict:
    """Adapt the repository's plain single-page P/T net format; reject extensions."""
    root = parse_xml(raw, 1_000_000)
    allowed = {
        "pnml": {"net"},
        "net": {"name", "page", "finalmarkings"},
        "page": {"place", "transition", "arc"},
        "place": {"name", "initialMarking", "text"},
        "transition": {"name"},
        "arc": {"inscription"},
        "name": {"text"},
        "initialMarking": {"text"},
        "inscription": {"text"},
        "finalmarkings": {"marking"},
        "marking": {"place"},
        "text": set(),
    }
    if root.tag != "pnml" or any(
        node.tag not in allowed or any(child.tag not in allowed[node.tag] for child in node)
        for node in root.iter()
    ):
        raise ValueError("unsupported PNML structure")
    net = root.find("net")
    if (
        len(root) != 1
        or net is None
        or net.get("type") != "http://www.pnml.org/version-2009/grammar/pnmlcoremodel"
    ):
        raise ValueError("one ordinary PNML net required")
    pages, finals = net.findall("page"), net.findall("finalmarkings")
    if len(pages) != 1 or len(finals) != 1 or len(finals[0]) != 1:
        raise ValueError("one page and final marking required")
    page = pages[0]
    places = page.findall("place")
    ids = [node.get("id") for node in page]
    if any(not key for key in ids) or len(set(ids)) != len(ids):
        raise ValueError("missing or duplicate PNML identity")
    indices = {node.get("id"): i for i, node in enumerate(places)}
    if not places or len(places) > 256 or len(page) > 4096:
        raise ValueError("PNML size limit exceeded")

    def number(value: str | None) -> int:
        if value is None or not re.fullmatch(r"[0-9]{1,6}", value.strip()):
            raise ValueError("invalid PNML token count")
        return int(value)

    initial, final = [0] * len(places), [0] * len(places)
    for i, place in enumerate(places):
        marking = place.findall("initialMarking")
        if len(marking) > 1 or place.find("text") is not None:
            raise ValueError("invalid initial marking")
        if marking:
            initial[i] = number(marking[0].findtext("text"))
    seen = set()
    for place in finals[0][0]:
        key = place.get("idref")
        if key not in indices or key in seen or len(place) != 1:
            raise ValueError("invalid final marking place")
        seen.add(key)
        final[indices[key]] = number(place.findtext("text"))
    if not sum(final):
        raise ValueError("nonempty final marking required")
    transitions = {
        t.get("id"): ([0] * len(places), [0] * len(places)) for t in page.findall("transition")
    }
    for arc in page.findall("arc"):
        source, target = arc.get("source"), arc.get("target")
        inscriptions = arc.findall("inscription")
        if len(inscriptions) > 1:
            raise ValueError("multiple arc weights")
        weight = number(inscriptions[0].findtext("text")) if inscriptions else 1
        if not weight:
            raise ValueError("zero arc weight")
        if source in indices and target in transitions:
            transitions[target][0][indices[source]] += weight
        elif source in transitions and target in indices:
            transitions[source][1][indices[target]] += weight
        else:
            raise ValueError("non-bipartite or dangling arc")
    return reachability(
        tuple(initial), tuple(final), transitions, max_states=max_states, max_tokens=max_tokens
    )
