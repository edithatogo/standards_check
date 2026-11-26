"""Advisory counterexamples for conditional source-clause identity."""

from __future__ import annotations

import hashlib
import json
import re
from itertools import combinations, product

from .source_applicability import evaluate_seed
from .task_framing import compile_witness

REVIEW = "source_text_corroborated_not_independent_adjudication"
HOLD = "held_independent_scope_and_fact_review"
FIELDS = {
    "id",
    "parent_item",
    "condition_atom",
    "source_anchor",
    "line",
    "review_status",
    "text_sha256",
}


def _pair(a, b):
    """Assume distinct reporting atoms; not an independently validated semantic model."""
    ac, bc = (f"condition:{row['condition_atom']}" for row in (a, b))
    ar, br = (f"obligation:{row['id']}" for row in (a, b))
    atoms = sorted({ac, bc, ar, br})
    witnesses = {}
    for values in product((True, False), repeat=len(atoms)):
        world = dict(zip(atoms, values, strict=True))
        left, right = not world[ac] or world[ar], not world[bc] or world[br]
        name = {(True, False): "a_only", (False, True): "b_only", (True, True): "both"}.get(
            (left, right)
        )
        if name is not None:
            witnesses.setdefault(name, world)
    relation = compile_witness(
        *("yes" if key in witnesses else "no" for key in ("a_only", "b_only", "both"))
    )
    return {
        "a": a["id"],
        "b": b["id"],
        "same_trigger": ac == bc,
        "same_parent": a["parent_item"] == b["parent_item"],
        "relation": relation,
        "witnesses": witnesses,
    }


def audit_projection(rows):
    """Compare candidate subclauses, retaining distinct content atoms and identities."""
    if not isinstance(rows, list) or not 1 <= len(rows) <= 64:
        raise ValueError("bounded candidate projection required")
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("invalid projection fields")
        if row["review_status"] != REVIEW:
            raise ValueError("candidate review state required")
        if (
            any(not isinstance(row[key], str) or not row[key].strip() for key in FIELDS - {"line"})
            or type(row["line"]) is not int
            or row["line"] < 1
            or not re.fullmatch(r"[0-9a-f]{64}", row["text_sha256"])
        ):
            raise ValueError("invalid projection record")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate candidate identity")
    pairs = [_pair(a, b) for a, b in combinations(rows, 2)]
    return {
        "binding": "projection_only",
        "assumption": "candidate condition implies its own reporting atom; distinct atoms independent",
        "admission": HOLD,
        "identity_controls": [_pair(row, row) for row in rows],
        "pairs": pairs,
        "condition_only_collisions": sum(row["same_trigger"] for row in pairs),
        "candidate_equivalences_distinct_ids": sum(
            row["relation"] == "equivalent" for row in pairs
        ),
    }


def audit_source(seed, pack_raw):
    """Reuse the source adapter with no manuscript facts; never infer nonapplicability."""
    bound = evaluate_seed(seed, pack_raw, b"\n")
    if bound["admission"] != HOLD or any(
        row["status"] != "unknown" for row in bound["subclauses"].values()
    ):
        raise ValueError("unexpected source-adapter status")
    items = {row["id"]: row for row in json.loads(pack_raw)["requirements"]}
    rows = [
        {
            **row,
            "text_sha256": hashlib.sha256(
                items[row["parent_item"]]["verbatim_text"].encode()
            ).hexdigest(),
        }
        for row in seed["clauses"]
    ]
    report = audit_projection(rows)
    return {
        **report,
        "binding": "source_adapter_verified",
        "source_pack_sha256": bound["source_pack_sha256"],
        "parent_items_retained": bound["parent_items_retained"],
        "projection": rows,
    }
