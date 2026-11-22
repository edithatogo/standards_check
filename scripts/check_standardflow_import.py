#!/usr/bin/env python3
"""Verify preserved legacy bytes and ancestry, not Rust parity or source rights."""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "conductor/tracks/03-standardflow-import/import.json"


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def check_import(root=ROOT):
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if (
        manifest["schema_version"] != "dev.standardflow.legacy-import.v1"
        or manifest["source_repository"] != "edithatogo/standardflow"
        or manifest["import_prefix"] != "legacy/standardflow"
    ):
        raise ValueError("Unexpected import contract, source repository or prefix")
    refs = manifest["source_refs"]
    if not isinstance(refs, dict) or not refs:
        raise ValueError("source_refs must record the preserved source branch heads")
    revisions = [manifest["source_commit"], *refs.values()]
    if any(
        not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value)
        for value in [*revisions, manifest["source_tree"]]
    ):
        raise ValueError("All source revisions and trees must be full Git object IDs")
    prefix = manifest["import_prefix"]
    source_tree = git(root, "rev-parse", manifest["source_commit"] + "^{tree}")
    imported_tree = git(root, "rev-parse", "HEAD:" + prefix)
    if source_tree != manifest["source_tree"] or imported_tree != source_tree:
        raise ValueError("Imported tree differs from the pinned source tree")
    for revision in sorted(set(revisions)):
        try:
            git(root, "merge-base", "--is-ancestor", revision, "HEAD")
        except subprocess.CalledProcessError as error:
            raise ValueError(f"Source history is not preserved: {revision}") from error
    try:
        git(root, "diff", "--quiet", "--", prefix)
        git(root, "diff", "--cached", "--quiet", "HEAD", "--", prefix)
    except subprocess.CalledProcessError as error:
        raise ValueError("Imported subtree has tracked working-tree or index drift") from error
    return {
        "source_commit": manifest["source_commit"],
        "source_tree": source_tree,
        "import_prefix": prefix,
        "preserved_revisions": len(set(revisions)),
        "evidence": "exact imported tree and source ancestry; no Rust parity claim",
    }


if __name__ == "__main__":
    try:
        print(json.dumps(check_import(), indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f"StandardFlow import check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
