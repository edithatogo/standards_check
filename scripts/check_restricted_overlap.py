"""Private, exact restricted-source overlap gate for explicit release manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .orthogonal_checks import leakage
from .validate_dataset_release import decode, read_bound, safe_path


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


def qualify_release(release: dict, manifest: dict, root: Path) -> dict:
    """Require the scan to bind exactly the final staged package, not a sample."""
    package = safe_path(root, release["package_root"])
    expected = {
        (package / row["path"]).relative_to(root).as_posix(): row["sha256"]
        for row in release["files"]
    }
    rows = manifest["artifacts"]
    observed = {row["artifact"]["path"]: row["artifact"]["sha256"] for row in rows}
    if len(observed) != len(rows) or observed != expected:
        raise ValueError("overlap artifact inventory differs from release")
    private = [row["text"]["path"] for row in manifest["references"]]
    private.extend(row["fragments"]["path"] for row in rows)
    if any(safe_path(root, path).resolve().is_relative_to(package.resolve()) for path in private):
        raise ValueError("private overlap inputs must not be staged for export")
    result = scan(manifest, root)
    if result["status"] != "clear_in_scope":
        raise ValueError("restricted overlap gate held")
    return {
        "status": result["status"],
        "artifacts": len(expected),
        "reference_count": result["reference_count"],
        "n": result["n"],
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
