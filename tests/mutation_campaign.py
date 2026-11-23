#!/usr/bin/env python3
"""Run ten hand-selected schema/API mutations in an isolated source copy.

This bounded contract campaign is not a repository-wide mutation score. Existing
regressions must pass first. Each exact mutation site must occur once; assertion
failures alone count as kills. Survivors, syntax/runtime errors, skips and timeouts
fail the campaign and remain distinct in its JSON report and retained logs.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    "python": [sys.executable, "-B", "-m", "unittest", "-v",
               "tests.test_validate_packs", "tests.test_mutation_campaign"],
    "api": ["node", "--test", "--test-reporter=tap", "api/test/corpus.test.js", "api/test/cors.test.js"],
}
# Each operator disables or changes one observable contract. Literal matching
# deliberately fails closed when the production site changes.
MUTATIONS = (
    ("required-title", "python", "schemas/standard-pack.v1.schema.json",
     '    "title",\n', ""),
    ("duplicate-requirement-id", "python", "scripts/validate_packs.py",
     "if len(requirement_ids) != len(set(requirement_ids)):", "if False:"),
    ("declared-pack-directory", "python", "scripts/validate_packs.py",
     "if pack_root != expected:", "if False:"),
    ("pack-symlink", "python", "scripts/validate_packs.py",
     "if path.is_symlink():", "if False:"),
    ("api-invalid-id", "api", "api/server.js",
     "if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(checklistId)) {", "if (false) {"),
    ("api-unknown-status", "api", "api/server.js",
     "res.status(404).json({ error: 'Checklist not found' });",
     "res.status(200).json({ error: 'Checklist not found' });"),
    ("api-list-error-status", "api", "api/server.js",
     "res.status(500).json({ error: 'Failed to fetch checklists' });",
     "res.status(200).json({ error: 'Failed to fetch checklists' });"),
    ("api-item-error-status", "api", "api/server.js",
     "res.status(500).json({ error: 'Failed to fetch checklist' });",
     "res.status(200).json({ error: 'Failed to fetch checklist' });"),
    ("api-origin-allowlist", "api", "api/cors-options.js",
     "origin: origins.length === 0 ? [DEFAULT_ORIGIN] : origins,", "origin: true,"),
    ("api-wildcard-config", "api", "api/cors-options.js",
     "if (origins.includes('*')) {", "if (false) {"),
)


def execute(command: list[str], cwd: Path, timeout: int) -> dict:
    started = time.monotonic()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", NODE_V8_COVERAGE="")
    try:
        with subprocess.Popen(command, cwd=cwd, env=environment, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              start_new_session=True) as process:
            try:
                output, _ = process.communicate(timeout=timeout)
                return {"exit_code": process.returncode, "output": output,
                        "seconds": round(time.monotonic() - started, 3), "timed_out": False}
            except subprocess.TimeoutExpired:
                # Node's test driver has child processes; stop the whole owned
                # session so a timed-out HTTP test cannot leave listeners behind.
                os.killpg(process.pid, signal.SIGKILL)
                output, _ = process.communicate()
                return {"exit_code": None, "output": output,
                        "seconds": round(time.monotonic() - started, 3), "timed_out": True}
    except OSError as error:
        return {"exit_code": None, "output": str(error),
                "seconds": round(time.monotonic() - started, 3), "timed_out": False}


def syntax_check(path: Path, workspace: Path, timeout: int) -> dict:
    if path.suffix == ".js":
        return execute(["node", "--check", str(path)], workspace, timeout)
    try:
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            ast.parse(content, filename=str(path))
        else:
            json.loads(content)
        return {"exit_code": 0, "output": "syntax valid", "timed_out": False}
    except (SyntaxError, ValueError) as error:
        return {"exit_code": 1, "output": str(error), "timed_out": False}


def classify(result: dict, group: str) -> str:
    if result["timed_out"]:
        return "timeout"
    if result["exit_code"] == 0:
        return "survived"
    if result["exit_code"] != 1:
        return "unviable"
    output = result["output"]
    if group == "python":
        assertion = bool(re.search(r"FAILED \(failures=[1-9][0-9]*\)", output))
        assertion = assertion and "AssertionError" in output and "ERROR: " not in output
    else:
        failures = re.search(r"^# fail ([0-9]+)$", output, re.MULTILINE)
        assertions = len(re.findall(r"^\s+code: 'ERR_ASSERTION'$", output, re.MULTILINE))
        assertion = failures is not None and int(failures[1]) == assertions > 0
        assertion = assertion and "failureType: 'hookFailed'" not in output
    return "assertion_kill" if assertion else "unviable"


def source_paths() -> list[Path]:
    paths = [ROOT / name for name in (
        "scripts/__init__.py", "scripts/validate_packs.py", "tests/__init__.py",
        "tests/test_validate_packs.py", "tests/test_mutation_campaign.py", "tests/mutation_campaign.py",
        "api/server.js", "api/cors-options.js",
        "api/package.json", "api/package-lock.json", "api/test/corpus.test.js", "api/test/cors.test.js",
    )]
    for directory in ("schemas", "packs/org.prisma/prisma/2020", "markdown/en"):
        paths.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    return sorted(paths)


def hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "target/mutation-evidence/report.json")
    parser.add_argument("--timeout", type=int, default=60, help="Per subprocess limit in seconds")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("this bounded campaign requires POSIX process-group cleanup")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    paths = source_paths()
    original_hashes = hashes(paths)
    report = {
        "schema_version": "dev.standardflow.bounded-mutation.v1",
        "scope": "ten hand-selected schema/API contract mutations; no global score",
        "base_commit": execute(["git", "rev-parse", "HEAD"], ROOT, 10)["output"].strip(),
        "python": sys.version.split()[0],
        "jsonschema": importlib.metadata.version("jsonschema"),
        "node": execute(["node", "--version"], ROOT, 10)["output"].strip(),
        "source_sha256": original_hashes,
        "commands": COMMANDS,
        "timeout_seconds": args.timeout,
        "baselines": {}, "mutations": [],
    }

    def record_log(name: str, result: dict) -> dict:
        log = args.output.parent / f"{name}.log"
        log.write_text(result["output"], encoding="utf-8")
        return {key: value for key, value in result.items() if key != "output"} | {"log": log.name}

    with tempfile.TemporaryDirectory(prefix="standardflow-mutations-") as temporary:
        workspace = Path(temporary)
        for path in paths:
            destination = workspace / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        shutil.copytree(ROOT / "api/node_modules", workspace / "api/node_modules", symlinks=True)
        for group, command in COMMANDS.items():
            result = execute(command, workspace, args.timeout)
            # A skipped symlink check is not a qualified baseline for that mutation.
            skipped = re.search(r"skipped=|^# skipped [1-9]", result["output"], re.MULTILINE)
            passed = result["exit_code"] == 0 and skipped is None
            report["baselines"][group] = record_log(f"baseline-{group}", result) | {"passed": passed}
        if all(result["passed"] for result in report["baselines"].values()):
            for name, group, relative, before, after in MUTATIONS:
                path = workspace / relative
                original = path.read_text(encoding="utf-8")
                if original.count(before) != 1:
                    report["mutations"].append({"id": name, "source": relative, "status": "source_site_drift"})
                    continue
                path.write_text(original.replace(before, after, 1), encoding="utf-8")
                try:
                    syntax = syntax_check(path, workspace, args.timeout)
                    if syntax["exit_code"] != 0:
                        result, status = syntax, "timeout" if syntax["timed_out"] else "unviable"
                    else:
                        result = execute(COMMANDS[group], workspace, args.timeout)
                        status = classify(result, group)
                    report["mutations"].append({
                        "id": name, "source": relative, "before": before, "after": after,
                        "status": status, "syntax_valid": syntax["exit_code"] == 0,
                        **record_log(name, result),
                    })
                    print(f"{name}: {status}", flush=True)
                finally:
                    path.write_text(original, encoding="utf-8")
    report["original_sources_unchanged"] = original_hashes == hashes(paths)
    report["outcomes"] = dict(Counter(item["status"] for item in report["mutations"]))
    report["passed"] = (all(result["passed"] for result in report["baselines"].values())
                        and len(report["mutations"]) == len(MUTATIONS)
                        and report["outcomes"] == {"assertion_kill": len(MUTATIONS)}
                        and report["original_sources_unchanged"])
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Report: {args.output}; passed={report['passed']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
