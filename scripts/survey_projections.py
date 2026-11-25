"""Versioned discovery and acquisition evidence, never a canonical pack."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

SCHEMA_VERSION = "dev.standardflow.equator-analytical-snapshot.v1"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
ID = re.compile(r"equator:[a-z0-9][a-z0-9._-]*")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def indexed(rows, key):
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError("duplicate evidence identity")
    return result


def project_survey(catalogue, survey, retrospective):
    revision = catalogue["source_revision"]
    if (
        not HEX40.fullmatch(revision)
        or survey["source_revision"] != revision
        or survey["summary"]["canonical_packs_promoted"] != 0
        or retrospective["canonical_packs_promoted"] != 0
    ):
        raise ValueError("incompatible source revision or admission boundary")
    declared = indexed(catalogue["guidelines"], "id")
    observed = indexed(survey["records"], "id")
    if (
        declared.keys() != observed.keys()
        or len(declared) != catalogue["published_count"]
        or len(declared) != survey["summary"]["published_count"]
    ):
        raise ValueError("catalogue/survey coverage mismatch")
    tables = {
        name: []
        for name in ("catalogue_identity", "acquisitions", "acquisition_items", "review_findings")
    }
    for identity, row in sorted(declared.items()):
        obs = observed[identity]
        if (
            not ID.fullmatch(identity)
            or not HEX40.fullmatch(row["source_blob_sha"])
            or row["source_blob_sha"] != obs["source_blob_sha"]
            or row["page_url"]
            != "https://equator-network.org/reporting-guidelines/" + identity.split(":", 1)[1] + "/"
        ):
            raise ValueError("invalid or mismatched directory identity")
        status = obs["status"]
        conflict = bool(obs.get("provider_disagreements")) or status in {
            "identifier_conflict",
            "ambiguous_identifier",
        }
        tables["catalogue_identity"].append(
            {
                "key": identity,
                "source_revision": revision,
                "source_blob_sha": row["source_blob_sha"],
                "page_url": row["page_url"],
                "metadata_status": row["metadata_status"],
                "title": row.get("title"),
                "acronym": row.get("acronym"),
                "declared_doi": row.get("doi"),
                "declared_pmid": row.get("pmid"),
                "study_types_json": json.dumps(row.get("study_types", []), ensure_ascii=False),
                "clinical_areas_json": json.dumps(
                    row.get("clinical_areas", []), ensure_ascii=False
                ),
                "report_sections_json": json.dumps(
                    row.get("report_sections", []), ensure_ascii=False
                ),
                "lookup_status": status,
                "resolved_doi": obs.get("resolved_doi"),
                "resolved_pmid": obs.get("resolved_pmid"),
                "pmcid": obs.get("pmcid"),
                "lookup_origin": obs.get("lookup_origin"),
                "identity_conflict": conflict,
                "rights_status": "unassessed",
                "disposition": "held_identity_conflict" if conflict else "discovery_only",
            }
        )
    editions = indexed(
        survey.get("priority_articles", []) + survey.get("bulk_articles", []), "edition"
    )
    for edition, row in sorted(editions.items()):
        if row.get("canonical_packs_promoted") != 0:
            raise ValueError("candidate acquisition cannot promote")
        tables["acquisitions"].append(
            {
                "key": edition,
                "doi": row.get("doi"),
                "pmcid": row.get("pmcid"),
                "source_sha256": row.get("source_sha256"),
                "status": row["status"],
                "disposition": "held_review",
                "expected_rows": row.get("expected_rows"),
                "matched_rows": row.get("matched_rows"),
                "rights_status": "unassessed",
            }
        )
        for table_no, table in enumerate(row.get("tables", []), 1):
            for item_no, item in enumerate(table.get("items", []), 1):
                digest = item.get("normalized_text_sha256")
                if not isinstance(digest, str) or not HEX64.fullmatch(digest):
                    raise ValueError("missing item fingerprint")
                tables["acquisition_items"].append(
                    {
                        "key": f"{edition}/{table_no}/{item_no}",
                        "edition": edition,
                        "table_id": table.get("table_id"),
                        "item_id": item["item_id"],
                        "source_anchor": item["source_anchor"],
                        "fingerprint": digest,
                        "disposition": "held_review",
                    }
                )
    for finding in retrospective["findings"]:
        code, record = finding["code"], finding["record"]
        tables["review_findings"].append(
            {"key": sha(json.dumps([code, record]).encode()), "code": code, "record": record}
        )
    return tables


SCHEMAS = {
    "catalogue_identity": {
        **dict.fromkeys(
            (
                "key",
                "source_revision",
                "source_blob_sha",
                "page_url",
                "metadata_status",
                "title",
                "acronym",
                "declared_doi",
                "declared_pmid",
                "study_types_json",
                "clinical_areas_json",
                "report_sections_json",
                "lookup_status",
                "resolved_doi",
                "resolved_pmid",
                "pmcid",
                "lookup_origin",
                "rights_status",
                "disposition",
            ),
            "str",
        ),
        "identity_conflict": "bool",
    },
    "acquisitions": {
        **dict.fromkeys(
            ("key", "doi", "pmcid", "source_sha256", "status", "disposition", "rights_status"),
            "str",
        ),
        "expected_rows": "int",
        "matched_rows": "int",
    },
    "acquisition_items": dict.fromkeys(
        ("key", "edition", "table_id", "item_id", "source_anchor", "fingerprint", "disposition"),
        "str",
    ),
    "review_findings": dict.fromkeys(("key", "code", "record"), "str"),
}


def validate(tables):
    from .source_reconciliation import validate_table_shapes

    keys = validate_table_shapes(tables, SCHEMAS)
    if any(row["edition"] not in keys["acquisitions"] for row in tables["acquisition_items"]):
        raise ValueError("unbound acquisition item")
    for row in tables["catalogue_identity"]:
        if (
            row["rights_status"] != "unassessed"
            or type(row["identity_conflict"]) is not bool
            or row["disposition"]
            != ("held_identity_conflict" if row["identity_conflict"] else "discovery_only")
            or (
                row["lookup_status"] in {"identifier_conflict", "ambiguous_identifier"}
                and not row["identity_conflict"]
            )
        ):
            raise ValueError("discovery status must not authorize use")
    if any(
        row["disposition"] != "held_review"
        for name in ("acquisitions", "acquisition_items")
        for row in tables[name]
    ):
        raise ValueError("acquisition must remain held")
    counts = Counter()
    anchors = set()
    for row in tables["acquisition_items"]:
        identity = (row["edition"], row["source_anchor"])
        if (
            not row["item_id"]
            or not row["table_id"]
            or not row["source_anchor"]
            or not isinstance(row["fingerprint"], str)
            or not HEX64.fullmatch(row["fingerprint"])
            or identity in anchors
        ):
            raise ValueError("invalid or repeated acquisition item evidence")
        counts[row["edition"]] += 1
        anchors.add(identity)
    for row in tables["acquisitions"]:
        count = counts[row["key"]]
        matched, expected = row["matched_rows"], row["expected_rows"]
        if row["rights_status"] != "unassessed":
            raise ValueError("acquisition rights must remain unassessed")
        if (
            matched is not None
            and matched != count
            or count
            and matched is None
            or expected is not None
            and (expected < 0 or count > expected)
            or row["status"] == "expected_numbered_rows_observed"
            and (not count or expected != count)
        ):
            raise ValueError("acquisition item count mismatch")
        if (count or row["source_sha256"] is not None) and (
            not isinstance(row["source_sha256"], str) or not HEX64.fullmatch(row["source_sha256"])
        ):
            raise ValueError("missing or invalid acquired source fingerprint")


def main():
    import argparse
    from pathlib import Path

    from .source_reconciliation import write_parquet

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, required=True)
    parser.add_argument("--survey", type=Path, required=True)
    parser.add_argument("--retrospective", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument(
        "--origin", choices=("scheduled_or_live", "historical_replay"), required=True
    )
    args = parser.parse_args()
    if not HEX40.fullmatch(args.revision):
        raise ValueError("exact producer revision required")
    data = {}
    hashes = {}
    for name in ("catalogue", "survey", "retrospective"):
        path = getattr(args, name)
        with path.open("rb") as handle:
            raw = handle.read(30_000_001)
        if len(raw) > 30_000_000:
            raise ValueError("receipt exceeds size budget")
        data[name], hashes[name] = json.loads(raw), sha(raw)
    if data["retrospective"].get("receipt_sha256") != hashes["survey"]:
        raise ValueError("retrospective is not bound to survey bytes")
    tables = project_survey(data["catalogue"], data["survey"], data["retrospective"])
    result = write_parquet(tables, args.output, schemas=SCHEMAS, validator=validate)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "producer_repository": "edithatogo/standards_check",
        "producer_revision": args.revision,
        "source_revision": data["catalogue"]["source_revision"],
        "input_sha256s": hashes,
        "origin": args.origin,
        "canonical_packs_promoted": 0,
        "claim_boundary": "Discovery and candidate evidence only; no rights, pack, applicability, or methodological approval.",
        **result,
    }
    (args.output / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({name: row["rows"] for name, row in result["tables"].items()}, sort_keys=True))


if __name__ == "__main__":
    main()
