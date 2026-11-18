#!/usr/bin/env python3
"""Validate costing reconciliation metadata and its evidence/coverage boundaries.

Uses only the Python standard library. This validates catalogue consistency,
not source accuracy, methodological quality, or the clinical/economic model.
"""

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


STATUSES = {
    "published_current_identified", "published_established", "published",
    "legacy", "superseded", "protocol_only_verified",
}
CATEGORIES = {
    "reporting_guideline", "reporting_guideline_extension",
    "methods_reporting_reference_case", "costing_reporting_framework",
    "sector_costing_standard", "measurement_valuation_tool",
    "sector_reporting_guideline", "appraisal_instrument",
    "model_appraisal_guidance", "validation_reporting_instrument",
    "historical_reporting_review_guidance", "historical_reporting_guideline",
    "development_protocol", "evidence_review", "study_protocol",
}
COVERAGE = {
    "all_numbered_items", "all_numbered_principles",
    "supplemental_items_only", "not_item_mapped",
}
IDENTIFIER = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
TRANSIENT_REF = re.compile(r"\bturn\d+(?:search|view|fetch)\d+\b")


def validate(registry, mapping_document):
    """Return actionable errors; an empty list means metadata is consistent."""
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    def valid_url(value):
        parsed = urlparse(value) if isinstance(value, str) else None
        return parsed is not None and parsed.scheme == "https" and bool(parsed.netloc)

    def valid_date(value):
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    for label, document in (("registry", registry), ("mappings", mapping_document)):
        check(document.get("schema_version") == "0.1.0", f"{label}: unsupported schema_version")
        serialized = json.dumps(document)
        check("retrieval_refs" not in serialized and not TRANSIENT_REF.search(serialized),
              f"{label}: transient retrieval references must be replaced with source URLs")
        check(bool(document.get("provenance")), f"{label}: missing provenance")

    sources = registry.get("instruments", [])
    domains = registry.get("domains", [])
    mappings = mapping_document.get("mappings", [])
    source_ids = [source.get("id") for source in sources]
    domain_ids = [domain.get("id") for domain in domains]
    check(bool(sources) and len(set(source_ids)) == len(source_ids), "instrument IDs must be nonempty and unique")
    check(bool(domains) and len(set(domain_ids)) == len(domain_ids), "domain IDs must be nonempty and unique")
    for identifier in source_ids + domain_ids:
        check(isinstance(identifier, str) and bool(IDENTIFIER.fullmatch(identifier)), f"invalid ID: {identifier!r}")
    source_by_id = {source.get("id"): source for source in sources}
    domain_id_set = set(domain_ids)
    snapshot = valid_date(registry.get("searched_through"))
    check(snapshot is not None, "registry: searched_through must be an ISO date")
    check(registry.get("not_a_consensus_standard") is True, "registry must disclose that this is not a consensus standard")
    check(bool(registry.get("coverage_statement")), "registry: missing coverage limitations")
    check(mapping_document.get("mapping_status") == "research_seed_review_required", "mappings must retain their review-required status")

    for source in sources:
        sid = source.get("id")
        check(source.get("category") in CATEGORIES, f"{sid}: unknown category")
        check(source.get("status") in STATUSES, f"{sid}: unknown status")
        check(valid_url(source.get("primary_url")), f"{sid}: missing/invalid primary HTTPS URL")
        checked = valid_date(source.get("checked_on"))
        check(checked is not None and (snapshot is None or checked <= snapshot), f"{sid}: invalid verification date")
        check(bool(source.get("domains")) and set(source.get("domains", [])) <= domain_id_set, f"{sid}: unknown/missing domain")
        if source.get("category") == "development_protocol":
            check(source.get("status") == "protocol_only_verified", f"{sid}: development protocol must not be classified as a completed guideline")
        if source.get("status") == "protocol_only_verified":
            check(source.get("category") == "development_protocol", f"{sid}: protocol status/category mismatch")
        if source.get("status") == "superseded":
            check(source.get("superseded_by") in source_by_id, f"{sid}: superseded record lacks a known successor")
        for relation in ("extends", "supersedes", "derives_from"):
            for target in source.get(relation, []):
                check(target in source_by_id and target != sid, f"{sid}: invalid {relation} target {target!r}")
        scope = source.get("verification_scope", {})
        check(scope.get("mapping_coverage") in COVERAGE, f"{sid}: missing/unknown verification scope")
        check(scope.get("full_checklist_transcription_added") is False, f"{sid}: this metadata catalogue cannot claim a full transcription")

    keys = []
    counts = Counter()
    for mapping in mappings:
        sid = mapping.get("instrument_id")
        item = mapping.get("item_id")
        keys.append((sid, item))
        counts[sid] += 1
        check(sid in source_by_id, f"mapping {sid}:{item}: unknown source")
        check(isinstance(item, str) and bool(item.strip()), f"mapping {sid}: missing original item identifier")
        check(mapping.get("item_identifier_verified") is True, f"mapping {sid}:{item}: identifier is not verified")
        check(mapping.get("relation") == "covers_topic", f"mapping {sid}:{item}: unsupported equivalence/relationship")
        mapped_domains = mapping.get("domain_ids", [])
        check(bool(mapped_domains) and set(mapped_domains) <= domain_id_set, f"mapping {sid}:{item}: unknown/missing domain")
        check(len(mapped_domains) == len(set(mapped_domains)), f"mapping {sid}:{item}: duplicate domains")
        check(valid_url(mapping.get("source_url")) and bool(mapping.get("source_locator")), f"mapping {sid}:{item}: missing source URL/locator")
        check(valid_date(mapping.get("checked_on")) is not None, f"mapping {sid}:{item}: invalid verification date")
    check(len(keys) == len(set(keys)), "duplicate source/item mapping IDs")

    for source in sources:
        sid = source.get("id")
        actual = counts[sid]
        scope = source.get("verification_scope", {})
        coverage = scope.get("mapping_coverage")
        declared = scope.get("verified_mapping_count")
        check(type(declared) is int and declared >= 0 and declared == actual, f"{sid}: verified mapping count differs from actual {actual}")
        check(source.get("item_level_verified") is (actual > 0), f"{sid}: item-level verification flag/count mismatch")
        if coverage == "not_item_mapped":
            check(actual == 0, f"{sid}: unmapped source unexpectedly contains verified mappings")
        elif coverage == "supplemental_items_only":
            check(actual == source.get("additional_items"), f"{sid}: supplemental item count mismatch")
        elif coverage in {"all_numbered_items", "all_numbered_principles"}:
            check(actual == source.get("count"), f"{sid}: complete identifier coverage disagrees with source count")
        if source.get("status") == "protocol_only_verified":
            check(actual == 0, f"{sid}: draft protocol must not supply verified final requirements")

    summary = registry.get("verification_summary", {})
    expected = {
        "instrument_count": len(sources), "domain_count": len(domains),
        "verified_mapping_count": len(mappings), "mapped_instrument_count": len(counts),
        "mapping_counts": dict(counts), "full_checklist_transcriptions_added": 0,
    }
    for field, value in expected.items():
        check(summary.get(field) == value, f"verification_summary.{field}: expected {value!r}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogue", nargs="?", type=Path,
                        default=Path(__file__).resolve().parents[1] / "reconciliations" / "costing")
    args = parser.parse_args()
    try:
        registry = json.loads((args.catalogue / "costing-standards-registry.json").read_text(encoding="utf-8"))
        mappings = json.loads((args.catalogue / "costing-item-mappings.json").read_text(encoding="utf-8"))
        errors = validate(registry, mappings)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"[ERROR] Cannot validate costing reconciliation: {exc}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"[ERROR] {error}", file=sys.stderr)
    if errors:
        return 1
    summary = registry["verification_summary"]
    print("Costing reconciliation passed: "
          f"{summary['instrument_count']} sources, {summary['domain_count']} domains, "
          f"{summary['verified_mapping_count']} verified identifier mappings. "
          "No complete checklist transcriptions are claimed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
