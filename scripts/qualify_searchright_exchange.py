"""Bounded synthetic exchange experiment; not a production adapter or authority."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(value):
    """Digest of this experiment's sorted, compact JSON, not a canonical pack lock."""
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def check(relative, value):
    schema = json.loads((ROOT / relative).read_bytes())
    require(
        Draft202012Validator(schema, format_checker=FormatChecker()).is_valid(value),
        "exchange schema mismatch",
    )


def receipt(source, view, mapping, companion_fields):
    return {
        "mapping": mapping,
        "status": "candidate_only",
        "source_sha256": digest(source),
        "view_sha256": digest(view),
        "companion_fields": companion_fields,
        "view": view,
    }


def cleared_fixture(rights):
    return rights["status"] == "cleared" and rights["spdx"] == "CC0-1.0"


def pack_view(source, *, expected_id, expected_version):
    """Produce only a synthetic reporting view; unmapped values stay in the source."""
    check("schemas/standard-pack.v1.schema.json", source)
    require(
        source["pack_id"] == expected_id and source["version"] == expected_version,
        "unexpected pack identity or version",
    )
    require(
        expected_id.startswith("example/")
        and source["kind"] == "reporting"
        and source["authority"]["source_url"] == "https://example.invalid/standard",
        "only the synthetic reporting lane is supported",
    )
    require(
        cleared_fixture(source["rights"])
        and source["verification"]["status"] == "source_reconciled",
        "unqualified fixture rights or verification",
    )
    rows = source["requirements"]
    require(len({row["id"] for row in rows}) == len(rows), "duplicate requirement ID")
    for row in rows:
        rights = row["rights"]
        require(
            rights == {"inherit_from_pack": True} or cleared_fixture(rights), "held item rights"
        )
    view = {
        "schema_version": "org.searchright.standard-pack.v1",
        "pack_id": source["pack_id"],
        "family": {"custom": "synthetic"},
        "version": source["version"],
        "source": source["authority"]["source_url"],
        "provenance_note": (
            "Synthetic candidate only; retain original pack and receipt. Crosswalks not mapped."
        ),
        "items": [
            {
                "item_id": row["id"],
                "label": row["display_number"] or row["id"],
                "requirement_summary": row["normalized_requirement"],
                "scope": "reporting",
                "crosswalks": [],
            }
            for row in rows
        ],
    }
    check("tests/fixtures/searchright-exchange/pack.schema.json", view)
    companion_fields = [
        "/schema_version",
        "/kind",
        "/title",
        "/authority",
        "/verification",
        "/rights",
    ]
    if "relationships" in source:
        companion_fields.append("/relationships")
    companion_fields += [
        f"/requirements/*/{field}"
        for field in (
            "display_number",
            "section",
            "verbatim_text",
            "guidance",
            "source_anchor",
            "rights",
            "evidence_expectations",
        )
    ]
    return receipt(source, view, "synthetic-pack-view.v1", companion_fields)


def safe_count(value):
    return type(value) is int and 0 <= value <= 2**53 - 1


def flow_view(source, *, expected_review, template):
    """Only an explicitly new database/register-only synthetic flow is representable."""
    check("tests/fixtures/searchright-exchange/flow.schema.json", source)
    require(template == "new_databases_registers", "unsupported or unknown review template")
    require(
        source["review_id"] == expected_review and expected_review.startswith("fixture:"),
        "unexpected review identity",
    )
    count_fields = set(source) - {"schema_version", "review_id", "full_text_exclusions"}
    require(all(safe_count(source[key]) for key in count_fields), "unsafe or noninteger count")
    require(source["records_other"] == 0, "other-source streams are not supported")
    reasons = source["full_text_exclusions"]
    require(
        all(
            safe_count(row["count"]) and row["count"] > 0 and row["label"].strip() for row in reasons
        ),
        "invalid reason",
    )
    require(
        len({row["reason_id"] for row in reasons}) == len(reasons)
        and len({row["label"].strip() for row in reasons}) == len(reasons),
        "duplicate reason",
    )
    field_map = {
        "records_databases": "databases",
        "records_registers": "registers",
        "duplicates_removed": "duplicate_records_removed",
        "automation_removed": "records_marked_ineligible_by_automation",
        "other_removed": "records_removed_other_reasons",
        "records_screened": "records_screened",
        "records_excluded": "records_excluded",
        "reports_sought": "reports_sought",
        "reports_not_retrieved": "reports_not_retrieved",
        "reports_assessed": "reports_assessed",
        "reports_included": "reports_included",
    }
    db = {target: source[key] for key, target in field_map.items()}
    db["reports_excluded"] = [{"reason": row["label"], "reports": row["count"]} for row in reasons]
    # Independent source-side conservation checks for this one bounded template.
    identified = source["records_databases"] + source["records_registers"]
    removed = sum(
        source[key] for key in ("duplicates_removed", "automation_removed", "other_removed")
    )
    excluded = sum(row["count"] for row in reasons)
    require(all(safe_count(value) for value in (identified, removed, excluded)), "unsafe aggregate")
    require(
        identified - removed == source["records_screened"]
        and source["records_screened"] - source["records_excluded"] == source["reports_sought"]
        and source["reports_sought"] - source["reports_not_retrieved"] == source["reports_assessed"]
        and excluded + source["reports_included"] == source["reports_assessed"]
        and source["studies_included"] <= source["reports_included"],
        "count conservation failure",
    )
    included = {"studies": source["studies_included"], "reports": source["reports_included"]}
    view = {
        "schema_version": "dev.standardflow.prisma-flow.v1",
        "review_id": expected_review,
        "template": template,
        "databases_registers": db,
        "other_methods": None,
        "previous_review": None,
        "new_included": included,
        "total_included": dict(included),
    }
    check("schemas/prisma-flow.v1.schema.json", view)
    return receipt(
        source,
        view,
        "synthetic-new-db-register-flow.v1",
        ["/schema_version", "/records_other", "/full_text_exclusions/*/reason_id"],
    )


def restore(source, candidate, expected_source_sha256, project):
    """Validate against an independently retained source pin; never reconstruct from the view."""
    require(digest(source) == expected_source_sha256, "retained source pin mismatch")
    require(digest(project(source)) == digest(candidate), "candidate view or receipt changed")
    return deepcopy(source)
