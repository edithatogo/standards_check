"""Bind a source-corroborated PRISMA conditional-clause seed to the rule engine."""

from __future__ import annotations

import hashlib
import json

from .applicability_rules import evaluate_bound


def evaluate_seed(seed: dict, pack_raw: bytes, facts_raw: bytes) -> dict:
    """Evaluate narrow subclauses, never discharge an entire parent requirement.

    Facts are explicit signed, evidence-bearing JSONL records. The caller must
    independently establish their truth and authority. The source seed is not
    an independently adjudicated or normative applicability specification.
    """
    if seed["schema_version"] != "dev.standardflow.source-conditional-clauses.v1":
        raise ValueError("unsupported clause seed")
    if seed["status"] != "source_corroborated_review_required":
        raise ValueError("unsupported source review state")
    source = seed["source"]
    if hashlib.sha256(pack_raw).hexdigest() != source["sha256"]:
        raise ValueError("source pack digest mismatch")
    pack = json.loads(pack_raw)
    if pack["pack_id"] != source["pack_id"] or pack["version"] != source["version"]:
        raise ValueError("source pack identity mismatch")
    if pack["authority"]["source_sha256"] != source["official_pdf_sha256"]:
        raise ValueError("source authority mismatch")
    items = {item["id"]: item for item in pack["requirements"]}
    lines = pack_raw.decode("utf-8").splitlines()
    decisions = []
    seen = set()
    atoms = set()
    for clause in seed["clauses"]:
        key, parent, atom = clause["id"], clause["parent_item"], clause["condition_atom"]
        if key in seen or parent not in items or key in items:
            raise ValueError("invalid or duplicate subclause identity")
        seen.add(key)
        atoms.add(atom)
        item = items[parent]
        if clause["source_anchor"] != item["source_anchor"]:
            raise ValueError("source item anchor mismatch")
        if clause["review_status"] != "source_text_corroborated_not_independent_adjudication":
            raise ValueError("source review state mismatch")
        line = clause["line"]
        if type(line) is not int or not 1 <= line <= len(lines):
            raise ValueError("invalid source line")
        record = json.loads("{" + lines[line - 1].strip().rstrip(",") + "}")
        if record != {"verbatim_text": item["verbatim_text"]}:
            raise ValueError("source line does not match item")
        anchor = {
            "source_id": "source-pack",
            "sha256": source["sha256"],
            "locator": f"line:{line}",
        }
        for action, literal in (("require", atom), ("exclude", "!" + atom)):
            decisions.append(
                {
                    "id": key + ":" + action,
                    "obligation": key,
                    "action": action,
                    "priority": 0,
                    "body": [literal],
                    "anchor": anchor,
                }
            )
    if not decisions or not 1 <= len(facts_raw) <= 1_000_000:
        raise ValueError("bounded fact and decision inventory required")
    facts = []
    fact_digest = hashlib.sha256(facts_raw).hexdigest()
    for index, line in enumerate(facts_raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict) or set(record) != {"literal", "evidence_id"}:
            raise ValueError("explicit fact evidence required")
        literal = record["literal"]
        if not isinstance(literal, str) or literal.removeprefix("!") not in atoms:
            raise ValueError("unknown fact atom")
        if not isinstance(record["evidence_id"], str) or not record["evidence_id"].strip():
            raise ValueError("fact evidence identity required")
        facts.append(
            {
                "id": f"fact:{index}",
                "literal": literal,
                "anchor": {
                    "source_id": "fact-evidence",
                    "sha256": fact_digest,
                    "locator": f"line:{index}",
                },
            }
        )
    sources = {"source-pack": pack_raw}
    if facts:
        sources["fact-evidence"] = facts_raw
    result = evaluate_bound(
        {
            "schema_version": "dev.standardflow.applicability-rules.v1",
            "facts": facts,
            "rules": [],
            "decisions": decisions,
        },
        sources,
    )
    return {
        "source_status": seed["status"],
        "parent_items_retained": sorted(items),
        "subclauses": result["obligations"],
        "fact_evidence_sha256": fact_digest,
        "source_pack_sha256": source["sha256"],
        "admission": "held_independent_scope_and_fact_review",
    }
