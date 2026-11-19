#!/usr/bin/env python3
"""Offline inventory and exact Conductor context validation (not rights clearance)."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PIN = "f06add33b598f4262a190f234828dda551db70d7"
AREAS = ("source", "markdown", "html", "pdf", "docx", "latex", "typst",
         "schemas", "tests", "crates", "packs")
LINK = re.compile(r"\]\((\.\.?/[^)#]+)(?:#[^)]*)?\)")
DEBT = re.compile(r"\[TBD\]|\bTODO\b|<kebab-case-id>", re.I)


def inventory(root, entries):
    counts = Counter()
    placeholders = []
    unreadable = []
    for path, mode, sha in entries:
        area = path.split("/", 1)[0]
        if area in AREAS:
            counts[area] += 1
        if area not in ("source", "markdown") or mode != "100644":
            continue
        if Path(path).suffix not in (".md", ".yml", ".yaml"):
            continue
        try:
            if DEBT.search((root / path).read_text(encoding="utf-8")):
                placeholders.append(path)
        except (OSError, UnicodeError):
            unreadable.append(path)
    return {"schema_version": "dev.standardflow.brownfield-inventory.v1",
            "tracked_files": len(entries), "areas": dict(sorted(counts.items())),
            "placeholder_paths": sorted(placeholders),
            "unreadable_text_paths": sorted(unreadable),
            "authority": "inventory_only", "rights_cleared": False,
            "source_reconciled": False, "output_parity_verified": False}


def context_errors(root, entries):
    index = {path: (mode, sha) for path, mode, sha in entries}
    errors = []
    if index.get(".agents/plugins/conductor") != ("160000", PIN):
        errors.append("Conductor exact gitlink is absent or different")
    modules = (root / ".gitmodules").read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*path\s*=\s*\.agents/plugins/conductor\s*$", modules):
        errors.append("Conductor gitmodules path invalid")
    if not re.search(r"(?m)^\s*url\s*=\s*https://github\.com/gemini-cli-extensions/conductor\.git\s*$", modules):
        errors.append("Conductor gitmodules URL invalid")
    if not (root / ".agents/skills/conductor/SKILL.md").is_file():
        errors.append("Conductor router skill missing")
    for name in ("index", "product", "tech-stack", "workflow", "roadmap", "tracks"):
        path = root / "conductor" / (name + ".md")
        if not path.is_file():
            errors.append("Missing Conductor context: " + name)
            continue
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            absolute = (path.parent / target).resolve()
            if not absolute.is_relative_to(root.resolve()) or not absolute.exists():
                errors.append("Broken Conductor link: " + name + " -> " + target)
    return sorted(errors)


def main():
    result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--stage", "-z"],
                            check=True, capture_output=True)
    entries = []
    for row in result.stdout.split(b"\0"):
        if not row:
            continue
        metadata, path = row.split(b"\t", 1)
        mode, sha, stage = metadata.decode("ascii").split()
        if stage != "0":
            raise ValueError("unmerged index entry")
        entries.append((path.decode("utf-8"), mode, sha))
    report = inventory(ROOT, entries)
    errors = context_errors(ROOT, entries)
    print(json.dumps({"inventory": report, "context_errors": errors},
                     indent=2, sort_keys=True))
    return int(bool(errors or report["unreadable_text_paths"]))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print("Foundation audit failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
