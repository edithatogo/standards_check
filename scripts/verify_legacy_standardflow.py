#!/usr/bin/env python3
"""Verify the retained legacy history and compare isolated source/subtree behaviour."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = (
    "prisma_data",
    "prisma_2020_updated_data",
    "consort_data",
    "consort_cluster_data",
    "strobe_data",
    "strobe_cohort_data",
)
CHECKLISTS = ("consort_checklist", "strobe_cohort_checklist", "stard_checklist")


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {command}\n{output}")
    return output


def verify_history() -> dict[str, object]:
    provenance = json.loads(
        run(
            [sys.executable, str(ROOT / "scripts/check_standardflow_import.py")],
            ROOT,
        )
    )
    if run(
        [
            "git",
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            str(provenance["import_prefix"]),
        ],
        ROOT,
    ):
        raise RuntimeError("The imported legacy subtree has uncommitted changes")
    return provenance


def exercise(root: Path, work: Path) -> dict[str, object]:
    work.mkdir()
    for directory in ("src", "schemas", "data", "tests", "web", "examples"):
        shutil.copytree(root / directory, work / directory)
    environment = os.environ.copy()
    # Verify the repaired module entry points without an inherited import workaround.
    environment.pop("PYTHONPATH", None)
    suite = run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        work,
        environment,
    )
    count = re.search(r"Ran (\d+) tests?", suite)
    if count is None or int(count.group(1)) != 52 or "skipped=" in suite:
        raise RuntimeError(f"Expected all 52 pinned legacy tests without skips\n{suite}")

    invalid_prisma = work / "invalid-prisma.svg"
    rejected = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            "generate",
            "data/invalid_prisma_data.json",
            "--output",
            str(invalid_prisma),
        ],
        cwd=work,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
    )
    validation_error = "'invalid_data' is not of type 'integer'"
    if rejected.returncode != 1 or validation_error not in rejected.stderr:
        raise RuntimeError("The invalid PRISMA fixture did not fail count validation")
    if invalid_prisma.exists():
        raise RuntimeError("The rejected PRISMA fixture produced output")

    outputs = work / "parity-outputs"
    outputs.mkdir()
    for fixture in (*DIAGRAMS, *CHECKLISTS):
        output = outputs / (f"{fixture}.svg" if fixture in DIAGRAMS else fixture)
        run(
            [
                sys.executable,
                "-m",
                "src.cli",
                "generate",
                f"data/{fixture}.json",
                "--output",
                str(output),
            ],
            work,
            environment,
        )
        if not output.exists():
            raise RuntimeError(f"CLI produced no output for {fixture}")

    files = {
        str(path.relative_to(outputs)): {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(outputs.rglob("*"))
        if path.is_file()
    }
    for fixture in CHECKLISTS:
        if not any(name.startswith(f"{fixture}/") for name in files):
            raise RuntimeError(f"Checklist {fixture} produced no section files")
    return {
        "tests": 52,
        "diagram_cases": list(DIAGRAMS),
        "checklist_cases": list(CHECKLISTS),
        "files": files,
        "invalid_prisma_fixture": {
            "exit_code": 1,
            "error": validation_error,
            "output_created": False,
        },
        "module_entrypoint_requires_pythonpath": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the JSON receipt to this path")
    arguments = parser.parse_args()
    provenance = verify_history()
    source_revision = str(provenance["source_commit"])
    source_tree = str(provenance["source_tree"])
    import_prefix = str(provenance["import_prefix"])
    graphviz = run(["dot", "-V"], ROOT).strip()
    imagemagick = run(["convert", "-version"], ROOT).splitlines()[0]
    with tempfile.TemporaryDirectory(prefix="standardflow-parity-") as temporary:
        temporary_root = Path(temporary)
        source = temporary_root / "source"
        source.mkdir()
        archive = subprocess.run(
            ["git", "archive", "--format=tar", source_revision],
            cwd=ROOT,
            check=True,
            capture_output=True,
            timeout=120,
        ).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
            tree.extractall(source, filter="data")
        baseline = exercise(source, temporary_root / "source-run")
        received = exercise(ROOT / import_prefix, temporary_root / "received-run")
        if baseline != received:
            raise RuntimeError("Source and received test counts or CLI output manifests differ")
    if verify_history() != provenance:
        raise RuntimeError("Import provenance changed during verification")
    requirements = ROOT / "requirements/legacy-standardflow.txt"
    packages = [
        line.split("==", 1)[0]
        for line in requirements.read_text().splitlines()
        if line and not line.startswith("#")
    ]
    receipt = {
        "result": "pass",
        "source_revision": source_revision,
        "source_tree": source_tree,
        "received_subtree": import_prefix,
        "received_tree": source_tree,
        "history_preserved": True,
        "preserved_revisions": provenance["preserved_revisions"],
        "python": sys.version.split()[0],
        "graphviz": graphviz,
        "imagemagick": imagemagick,
        "dependencies": {name: importlib.metadata.version(name) for name in packages},
        "claim": "same-environment source-to-subtree legacy behaviour parity",
        "claim_limits": [
            "not Rust replacement parity",
            "not scientific validation",
            "not accessibility certification",
            "not third-party content rights clearance",
            "legacy count validation is not comprehensive arithmetic or methodological validation",
        ],
        **received,
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
