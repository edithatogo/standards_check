"""Bounded signed ground-Horn applicability rules with explicit precedence.

This is a finite Datalog fragment, not a general Datalog or ASP interpreter.
Anchors declare provenance; the caller must independently verify their authority.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict

ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}")
VERSION = "dev.standardflow.applicability-rules.v1"


def _identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError("invalid identifier")


def _literal(value):
    if not isinstance(value, str):
        raise ValueError("invalid literal")
    _identifier(value.removeprefix("!"))


def _opposite(literal):
    return literal[1:] if literal.startswith("!") else "!" + literal


def _anchor(anchor):
    if not isinstance(anchor, dict) or set(anchor) != {"source_id", "sha256", "locator"}:
        raise ValueError("source anchor required")
    _identifier(anchor["source_id"])
    if not isinstance(anchor["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", anchor["sha256"]):
        raise ValueError("exact source digest required")
    if not isinstance(anchor["locator"], str) or not 1 <= len(anchor["locator"].strip()) <= 256:
        raise ValueError("bounded source locator required")


def _validate(doc):
    if not isinstance(doc, dict) or set(doc) != {"schema_version", "facts", "rules", "decisions"}:
        raise ValueError("invalid rule contract")
    if doc["schema_version"] != VERSION:
        raise ValueError("unsupported rule contract")
    fields = {
        "facts": {"id", "literal", "anchor"},
        "rules": {"id", "head", "body", "anchor"},
        "decisions": {"id", "obligation", "action", "priority", "body", "anchor"},
    }
    anchors = {}
    for kind, keys in fields.items():
        rows = doc[kind]
        if not isinstance(rows, list) or len(rows) > 256:
            raise ValueError("rule inventory exceeds bound")
        for row in rows:
            if not isinstance(row, dict) or set(row) != keys:
                raise ValueError("invalid rule record")
            _identifier(row["id"])
            _anchor(row["anchor"])
            if row["id"] in anchors:
                raise ValueError("duplicate rule or fact ID")
            anchors[row["id"]] = row["anchor"]
            if kind == "facts":
                _literal(row["literal"])
                continue
            if not isinstance(row["body"], list) or not 1 <= len(row["body"]) <= 32:
                raise ValueError("nonempty bounded rule body required")
            for literal in row["body"]:
                _literal(literal)
            if kind == "rules":
                _literal(row["head"])
            else:
                _identifier(row["obligation"])
                if row["action"] not in ("require", "exclude"):
                    raise ValueError("invalid obligation action")
                if type(row["priority"]) is not int or not 0 <= row["priority"] <= 1000:
                    raise ValueError("invalid precedence")
    if not doc["decisions"]:
        raise ValueError("no decision inventory")
    return anchors


def _closure(facts, rules, blocked):
    support = {}
    for row in sorted(facts, key=lambda r: r["id"]):
        literal = row["literal"]
        if literal.removeprefix("!") not in blocked:
            support.setdefault(literal, {row["id"]})
    rounds = 0
    while True:
        new = {}
        for row in sorted(rules, key=lambda r: r["id"]):
            head = row["head"]
            if head in support or head.removeprefix("!") in blocked:
                continue
            if all(literal in support for literal in row["body"]):
                proof = {row["id"]}.union(*(support[literal] for literal in row["body"]))
                new.setdefault(head, proof)
        if not new:
            return support, rounds
        support.update(new)
        rounds += 1


def evaluate(doc: dict) -> dict:
    """Conserve obligation identity; only explicit, supported exclusions are allowed."""
    anchors = _validate(doc)
    full, rounds = _closure(doc["facts"], doc["rules"], set())
    conflict = {literal.removeprefix("!") for literal in full if _opposite(literal) in full}
    clean, _ = _closure(doc["facts"], doc["rules"], conflict)
    tainted = {literal.removeprefix("!") for literal in set(full) - set(clean)}

    def state(body):
        if any(literal.removeprefix("!") in tainted for literal in body):
            return "held_conflict"
        if any(_opposite(literal) in clean for literal in body):
            return "false"
        if all(literal in clean for literal in body):
            return "true"
        return "unknown"

    grouped = defaultdict(lambda: defaultdict(list))
    for row in doc["decisions"]:
        grouped[row["obligation"]][row["priority"]].append(row)
    obligations = {}
    for obligation, levels in sorted(grouped.items()):
        result = {"status": "unknown", "rules": [], "support": []}
        for _, rows in sorted(levels.items(), reverse=True):
            active = [(row, state(row["body"])) for row in rows]
            active = [(row, status) for row, status in active if status != "false"]
            if not active:
                continue
            states = {status for _, status in active}
            actions = {row["action"] for row, status in active if status == "true"}
            proof = set()
            for row, status in active:
                if status == "true":
                    for literal in row["body"]:
                        proof.update(clean[literal])
            if "held_conflict" in states or len(actions) > 1:
                status = "held_conflict"
            elif "unknown" in states:
                status = "unknown"
            else:
                status = "required" if actions == {"require"} else "not_applicable"
            result = {
                "status": status,
                "rules": sorted(row["id"] for row, _ in active),
                "support": sorted(proof),
            }
            break
        obligations[obligation] = result
    return {
        "authority": "advisory_only",
        "rounds": rounds,
        "conflicted_atoms": sorted(conflict),
        "tainted_atoms": sorted(tainted),
        "obligations": obligations,
        "anchors": anchors,
    }


def evaluate_bound(doc: dict, sources: dict) -> dict:
    """Verify exact local bytes and line locators before advisory rule execution."""
    anchors = _validate(doc)
    expected = {anchor["source_id"] for anchor in anchors.values()}
    if set(sources) != expected:
        raise ValueError("source inventory differs from rule anchors")
    lines = {}
    digests = {}
    for key, raw in sources.items():
        if not isinstance(raw, bytes) or not 1 <= len(raw) <= 1_000_000:
            raise ValueError("invalid bounded source bytes")
        lines[key] = raw.decode("utf-8").splitlines()
        digests[key] = hashlib.sha256(raw).hexdigest()
    for anchor in anchors.values():
        key = anchor["source_id"]
        locator = re.fullmatch(r"line:([1-9][0-9]{0,6})", anchor["locator"])
        if anchor["sha256"] != digests[key] or locator is None:
            raise ValueError("source digest or locator mismatch")
        if int(locator.group(1)) > len(lines[key]):
            raise ValueError("source locator outside input")
    return {**evaluate(doc), "source_binding": "exact_bytes_and_line_locators"}
