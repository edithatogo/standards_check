"""Private, exact restricted-source overlap gate for explicit release manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .orthogonal_checks import leakage
from .validate_dataset_release import decode, read_bound


def _inventory(rows, expected, fields):
    if (
        not isinstance(rows, list)
        or not isinstance(expected, list)
        or not expected
        or len(expected) != len(set(expected))
        or any(not isinstance(row, dict) or set(row) != fields for row in rows)
    ):
        raise ValueError("invalid expected and supplied inventory")
    by_id = {row["id"]: row for row in rows}
    if len(by_id) != len(rows) or set(by_id) != set(expected):
        raise ValueError("incomplete or duplicate inventory")
    return by_id


def scan(manifest: dict, root: Path) -> dict:
    """Bind extracted text to exact inputs; do not echo paths, excerpts or source hashes.

    The independent inventory and extraction-completeness witness must be authorized
    outside this function. The receipt describes only the specified input universe.
    """
    fields = {
        "schema_version",
        "n",
        "expected_references",
        "expected_artifacts",
        "references",
        "artifacts",
    }
    if (
        set(manifest) != fields
        or manifest["schema_version"] != "dev.standardflow.restricted-overlap.v1"
    ):
        raise ValueError("invalid overlap manifest")
    references = _inventory(
        manifest["references"],
        manifest["expected_references"],
        {"id", "text"},
    )
    artifacts = _inventory(
        manifest["artifacts"],
        manifest["expected_artifacts"],
        {"id", "artifact", "fragments", "extraction_complete"},
    )
    if any(row["extraction_complete"] is not True for row in artifacts.values()):
        raise ValueError("incomplete extraction")
    if len(references) * len(artifacts) > 10_000:
        raise ValueError("inventory exceeds comparison limit")
    restricted = {
        key: read_bound(root, row["text"]).decode("utf-8") for key, row in references.items()
    }
    output = {}
    bound = {}
    for key, row in artifacts.items():
        read_bound(root, row["artifact"])
        bound[key] = row["artifact"]["sha256"]
        fragments = decode(read_bound(root, row["fragments"]))
        if not isinstance(fragments, list) or any(not isinstance(p, str) for p in fragments):
            raise ValueError("expected ordered extracted text fragments")
        output[key] = fragments
    result = leakage(restricted, output, n=manifest["n"])
    return {
        **result,
        "schema_version": manifest["schema_version"],
        "n": manifest["n"],
        "reference_count": len(restricted),
        "artifact_sha256": bound,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.manifest.stat().st_size > 1_000_000:
            raise ValueError("manifest size limit exceeded")
        result = scan(decode(args.manifest.read_bytes()), args.root)
    except (ValueError, TypeError, KeyError, OSError, AttributeError):
        # The input may contain restricted text. Never print exception contents.
        print(json.dumps({"status": "held_invalid_or_missing"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "clear_in_scope" else 1


if __name__ == "__main__":
    raise SystemExit(main())
