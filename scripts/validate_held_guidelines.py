#!/usr/bin/env python3
"""Audit held legacy arrays against independently sourced printed identifiers.

This is a narrow identity/copy check, not a Standard Pack admission gate. It
does not verify wording, rights, applicability or methodology. The preserved
inputs are known invalid candidates, so the default archive audit exits 1.
No network access or source-artifact redistribution is required.
"""

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/migration/standardflow/held-guidelines-qualification.json"


def items_digest(items):
    return hashlib.sha256(
        json.dumps(items, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def compare_items(items, expected_ids, stard_items):
    """Check printed IDs and copied STARD descriptions; do not attest new text."""
    if (
        not expected_ids
        or any(not isinstance(value, str) or not value for value in expected_ids)
        or len(set(expected_ids)) != len(expected_ids)
    ):
        raise ValueError("Source identifier fixture must contain unique nonempty strings")
    valid_array = isinstance(items, list) and bool(items)
    entries = items if isinstance(items, list) else []
    identifiers = []
    descriptions = []
    malformed = []
    for position, item in enumerate(entries, 1):
        if not isinstance(item, dict):
            malformed.append(position)
            continue
        identifier = item.get("id")
        description = item.get("description")
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or not isinstance(description, str)
            or not description.strip()
        ):
            malformed.append(position)
            continue
        identifiers.append(identifier)
        descriptions.append(" ".join(description.split()))
    counts = Counter(identifiers)
    missing = [identifier for identifier in expected_ids if identifier not in counts]
    unexpected = sorted(set(identifiers) - set(expected_ids))
    duplicates = sorted(identifier for identifier, count in counts.items() if count > 1)
    identifiers_match = bool(
        valid_array and not malformed and not missing and not unexpected and not duplicates
    )
    stard_descriptions = {" ".join(item["description"].split()) for item in stard_items}
    copied_descriptions = sum(value in stard_descriptions for value in descriptions)
    known_copy = bool(valid_array and copied_descriptions == len(entries))
    errors = []
    if not valid_array or malformed:
        errors.append("Expected a nonempty item array with string id and description fields")
    if not identifiers_match:
        errors.append("Printed identifiers do not match the independently sourced edition")
    if known_copy:
        errors.append("All descriptions are copied from STARD, even if IDs or count were changed")
    return {
        "scope": "printed_identifiers_and_known_stard_copy_only",
        "expected_items": len(expected_ids),
        "actual_items": len(entries),
        "identifiers_match": identifiers_match,
        "missing_identifiers": missing,
        "unexpected_identifiers": unexpected,
        "duplicate_identifiers": duplicates,
        "malformed_item_positions": malformed,
        "stard_description_matches": copied_descriptions,
        "known_stard_copy": known_copy,
        "errors": errors,
    }


def read_archive_json(revision, path):
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def audit_archive():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    sources = json.loads((ROOT / ledger["identifier_fixture"]).read_text(encoding="utf-8"))
    revision = ledger["archive_revision"]
    reference = read_archive_json(revision, ledger["reference_path"])["items"]
    if items_digest(reference) != ledger["reference_items_sha256"]:
        raise ValueError("Archived STARD reference does not match the recorded items digest")
    if not ledger["datasets"]:
        raise ValueError("No held datasets were specified")
    datasets = []
    for dataset in ledger["datasets"]:
        if not dataset["source_editions"]:
            raise ValueError(f"No source edition specified for {dataset['label']}")
        data = read_archive_json(revision, dataset["archive_path"])
        items = data.get("items")
        datasets.append(
            {
                "label": dataset["label"],
                "archive_path": dataset["archive_path"],
                "items_sha256": items_digest(items),
                "exact_stard_items_copy": items == reference,
                "comparisons": {
                    edition: compare_items(
                        items, sources["editions"][edition]["item_ids"], reference
                    )
                    for edition in dataset["source_editions"]
                },
            }
        )
    return {
        "archive_revision": revision,
        "scope": "Identity and known-copy audit only; no pack admission or source reconciliation",
        "datasets": datasets,
    }


def main():
    try:
        result = audit_archive()
    except subprocess.CalledProcessError:
        print(
            json.dumps(
                {
                    "error": "Historical Git source unavailable; fetch preserved primary history before auditing"
                }
            )
        )
        return 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return int(
        any(
            comparison["errors"]
            for dataset in result["datasets"]
            for comparison in dataset["comparisons"].values()
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
