"""Bounded, non-authoritative linguistic diagnostics for explicitly paired rows."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

if __package__:
    from .lexical_text import normalise
else:
    from lexical_text import normalise

MAX_CHARS = 8192
MAX_TOKENS = 1024
PATTERNS = {
    "modality": r"\b(?:must|shall|(?:is|are) required(?: to)?|required to|should|ought to|may|can|need not)\b",
    "negation": r"\b(?:not(?!\s+only\b)|never|neither|nor|no(?!\s+(?:more|fewer)\s+than\b)|without)\b|n[’']t\b",
    "quantification": r"(?<!\w)(?:at least|at most|no more than|no fewer than|more than|less than|up to|exactly|all|each|every|any|some|none|both|either|one|two|three|four|five|six|seven|eight|nine|ten|[+−-]?\d+(?:[.,]\d+)*(?:\s*%)?)(?!\w)",
    "logic": r"\b(?:and/or|not only|but also|and|or|not(?!\s+only\b)|neither|nor|except(?: when| if)?|unless|excluding|other than)\b",
    "conditionality": r"\b(?:where applicable|if applicable|as applicable|provided that|only if|if|unless|when|where|before|after|within|until|during|following|prior to|at the time of)\b",
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def span(kind: str, text: str, start: int, end: int) -> dict:
    return {
        "kind": kind,
        "start": start,
        "end": end,
        "sha256": digest(
            " ".join(unicodedata.normalize("NFKC", text[start:end]).casefold().split())
        ),
    }


def logic_grouping(text: str) -> dict:
    """Retain explicit coordination grouping, not an inferred Boolean expression."""
    stack, groups = [], []
    connectors = 0
    balanced = True
    for match in re.finditer(r"\(|\)|\b(?:and/or|and|or)\b", text, re.IGNORECASE):
        token = match.group()
        if token == "(":
            stack.append(connectors)
        elif token == ")":
            if not stack:
                balanced = False
                continue
            start = stack.pop()
            if connectors > start:
                groups.append([start, connectors])
        else:
            connectors += 1
    return {"groups": sorted(groups), "balanced": balanced and not stack}


def predicate_arguments(doc) -> list[dict]:
    """Compare bounded lemma roles; retain full source spans separately.

    Active subject and explicit passive agent are actor candidates. A passive
    subject is a patient candidate. Never supply an unexpressed actor. This is
    grammatical evidence, not complete semantic role labelling or entailment.
    """

    def argument(kind, token):
        # Ignore surface position and determiners; retain lexical modifiers.
        for member in (token, *token.conjuncts):
            modifiers = sorted(
                (c.dep_, c.lemma_.casefold())
                for c in member.children
                if c.dep_ in {"amod", "compound", "poss", "flat"}
            )
            yield (kind, digest(repr((member.lemma_.casefold(), modifiers))))

    predicates = []
    for verb in doc:
        if verb.pos_ != "VERB":
            continue
        args = []
        for child in verb.children:
            if child.dep_ in {"nsubj", "csubj"}:
                args.extend(argument("actor", child))
            elif child.dep_ in {
                "nsubjpass",
                "csubjpass",
                "nsubj:pass",
                "csubj:pass",
                "dobj",
                "obj",
            }:
                args.extend(argument("patient", child))
            elif child.dep_ in {"iobj", "dative"}:
                args.extend(argument("recipient", child))
            elif child.dep_ in {"attr", "oprd"}:
                args.extend(argument("complement", child))
            elif child.dep_ == "agent":
                for obj in child.children:
                    if obj.dep_ == "pobj":
                        args.extend(argument("actor", obj))
            elif child.dep_ == "obl:agent":
                args.extend(argument("actor", child))
        predicates.append(
            {
                "predicate_sha256": digest(verb.lemma_.casefold()),
                "arguments": [list(a) for a in sorted(args)],
            }
        )
    return sorted(predicates, key=lambda row: (row["predicate_sha256"], row["arguments"]))


def describe(text: str, nlp=None) -> dict:
    """Return hashes and character offsets, never input prose or lemma strings."""
    if len(text) > MAX_CHARS:
        raise ValueError("row outside linguistic bounds")
    words = normalise(text).split()
    if not words or len(words) > MAX_TOKENS:
        raise ValueError("row outside linguistic bounds")
    result = {"text_sha256": digest(text), "token_count": len(words), "syntax_status": "not_run"}
    for field, pattern in PATTERNS.items():
        cues = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            cue = span(field, text, *match.span())
            value = match.group().casefold()
            if field == "modality":
                cue["kind"] = (
                    "recommendation"
                    if value in {"should", "ought to"}
                    else "permission"
                    if value in {"may", "can"}
                    else "no_obligation"
                    if value == "need not"
                    else "obligation"
                )
            elif field == "logic":
                cue["kind"] = (
                    "and"
                    if value in {"and", "not only", "but also"}
                    else "or"
                    if value == "or"
                    else "and_or"
                    if value == "and/or"
                    else "not"
                    if value in {"not", "neither", "nor"}
                    else "exception"
                )
            if field == "conditionality":
                cue["kind"] = (
                    "temporal"
                    if value
                    in {
                        "before",
                        "after",
                        "within",
                        "until",
                        "during",
                        "following",
                        "prior to",
                        "at the time of",
                    }
                    else "applicability"
                )
                # Bounded clause candidate; not a logical parse or scope proof.
                end = re.search(r"[,;.!?\n]", text[match.end() :])
                stop = match.end() + end.start() if end else len(text)
                cue["scope_sha256"] = span("scope", text, match.start(), stop)["sha256"]
            cues.append(cue)
        result[field] = cues
    result["logic_grouping"] = logic_grouping(text)
    result["conditional_obligation_candidate"] = bool(
        result["conditionality"] and any(c["kind"] == "obligation" for c in result["modality"])
    )
    if nlp is None:
        return result
    from spacy.matcher import DependencyMatcher

    doc = nlp(text)
    if (
        doc.text != text
        or len(doc) > MAX_TOKENS
        or not all(
            doc.has_annotation(name, require_complete=True) for name in ("DEP", "POS", "LEMMA")
        )
    ):
        raise ValueError("missing or incomplete reference annotations")
    result["syntax_status"] = "parsed_reference"
    result["tokens"] = [
        dict(
            span("token", text, t.idx, t.idx + len(t)),
            lemma_sha256=digest(t.lemma_.casefold()),
            pos=t.pos_,
            dep=t.dep_,
            head=t.head.i,
        )
        for t in doc
    ]
    result["clauses"] = [span("sentence", text, s.start_char, s.end_char) for s in doc.sents]
    roles, negation = [], []
    matcher = DependencyMatcher(doc.vocab)
    matcher.add(
        "ARGUMENT",
        [
            [
                {"RIGHT_ID": "verb", "RIGHT_ATTRS": {"POS": "VERB"}},
                {
                    "LEFT_ID": "verb",
                    "REL_OP": ">",
                    "RIGHT_ID": "argument",
                    "RIGHT_ATTRS": {
                        "DEP": {
                            "IN": [
                                "nsubj",
                                "nsubjpass",
                                "csubj",
                                "dobj",
                                "obj",
                                "iobj",
                                "attr",
                                "oprd",
                                "neg",
                                "advcl",
                            ]
                        }
                    },
                },
            ]
        ],
    )

    def role(kind, token, head, subtree=False):
        start = token.left_edge.idx if subtree else token.idx
        last = token.right_edge if subtree else token
        return dict(
            span(kind, text, start, last.idx + len(last)),
            head=head.i,
            head_lemma_sha256=digest(head.lemma_.casefold()),
        )

    for token in doc:
        if token.pos_ == "VERB":
            roles.append(role("action", token, token))
    for _, (verb_id, arg_id) in matcher(doc):
        verb, arg = doc[verb_id], doc[arg_id]
        if arg.dep_ == "neg":
            negation.append(role("negation", arg, verb))
        elif arg.dep_ == "advcl":
            result["clauses"].append(role("dependent_clause", arg, verb, True))
        else:
            kind = "subject" if arg.dep_ in {"nsubj", "nsubjpass", "csubj"} else "object"
            roles.append(role(kind, arg, verb, True))
            if kind == "object" and verb.lemma_.casefold() in {
                "document",
                "record",
                "report",
                "submit",
                "retain",
            }:
                roles.append(role("evidence_candidate", arg, verb, True))
    result["semantic_roles"] = sorted(roles, key=lambda r: (r["start"], r["kind"], r["head"]))
    result["predicate_arguments"] = predicate_arguments(doc)
    result["dependency_negation"] = sorted(negation, key=lambda r: (r["start"], r["head"]))
    return result


def compare(left: str, right: str, nlp=None) -> dict:
    base = {"schema_version": 2, "canonical_packs_promoted": 0, "status": "held_input"}
    try:
        a, b = describe(left, nlp), describe(right, nlp)
    except ValueError:
        return base

    def signature(rows):
        return [{k: v for k, v in row.items() if k not in {"start", "end"}} for row in rows]

    fields = list(PATTERNS)
    if nlp is not None:
        fields += ["tokens", "clauses", "dependency_negation"]
    changed = [field for field in fields if signature(a[field]) != signature(b[field])]
    if a["logic_grouping"] != b["logic_grouping"] and "logic" not in changed:
        changed.append("logic")
    if nlp is not None and a["predicate_arguments"] != b["predicate_arguments"]:
        changed.append("semantic_roles")
    similarity = SequenceMatcher(
        None, normalise(left).split(), normalise(right).split(), autojunk=False
    ).ratio()
    return {
        **base,
        "status": "diagnostic_only",
        "lexical_similarity": round(similarity, 6),
        "exact_text_equal": left == right,
        "changed_fields": changed,
        "source": a,
        "candidate": b,
    }


def load_reference(path: Path):
    """Explicitly supplied trusted local English model only; never download."""
    import spacy

    if not path.is_dir():
        raise ValueError("a local model directory is required")
    model = spacy.load(path)
    if model.lang != "en":
        raise ValueError("only English reference models are supported")
    return model, {
        "spacy_version": spacy.__version__,
        "model_name": model.meta.get("name"),
        "model_version": model.meta.get("version"),
    }
