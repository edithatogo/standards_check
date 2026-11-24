#!/usr/bin/env python3
"""Check publication plan/receipt integrity offline; never certify scientific acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = Path("contracts/publication")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fields(value: object, names: str, label: str) -> dict:
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ValueError(f"{label}: missing or unknown fields")
    return value


def nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: nonempty text required")
    return value


def strings(value: object, label: str, *, allow_empty: bool = False) -> list:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ValueError(f"{label}: list required")
    for item in value:
        nonempty(item, label)
    require(len(value) == len(set(value)), f"{label}: duplicate values")
    return value


def hexadecimal(value: object, length: int, label: str) -> None:
    require(
        isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is not None,
        f"{label}: exact lowercase {length}-character hash required",
    )


def timestamp(value: object) -> datetime:
    parsed = datetime.fromisoformat(nonempty(value, "timestamp").replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "timestamp requires timezone")
    return parsed


def check_file(root: Path, reference: dict) -> None:
    path = Path(nonempty(reference.get("path"), "artifact path"))
    require(
        not path.is_absolute() and ".." not in path.parts,
        "artifact must use a repository-relative path without traversal",
    )
    resolved = (root / path).resolve()
    require(
        resolved.is_relative_to(root.resolve()) and resolved.is_file(),
        f"artifact absent or outside root: {path}",
    )
    hexadecimal(reference.get("sha256"), 64, "artifact sha256")
    with resolved.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    require(digest == reference["sha256"], f"artifact hash mismatch: {path}")


def design_digest(design: dict) -> str:
    raw = json.dumps(
        design, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate(contract: dict, root: Path = ROOT) -> dict:
    fields(contract, "schema_version status design freeze runs claims", "contract")
    require(
        contract["schema_version"] == "dev.standardflow.publication-contract.v1",
        "unsupported publication contract version",
    )
    status = contract["status"]
    require(status in ("planned", "frozen", "executed"), "invalid contract status")
    design = fields(
        contract["design"], "programme_id protocol experiments inputs freeze_blockers", "design"
    )
    nonempty(design["programme_id"], "programme_id")
    protocol = fields(design["protocol"], "version path sha256", "protocol")
    require(
        re.fullmatch(r"\d+\.\d+\.\d+", nonempty(protocol["version"], "protocol version"))
        is not None,
        "protocol needs an explicit version",
    )
    check_file(root, protocol)
    strings(design["freeze_blockers"], "freeze_blockers", allow_empty=True)
    require(isinstance(design["inputs"], list), "inputs must be a list")
    inputs, families, hashes = {}, {}, {}
    for item in design["inputs"]:
        fields(item, "id family partition path sha256", "input")
        identity = nonempty(item["id"], "input id")
        require(identity not in inputs, "duplicate input id")
        family = nonempty(item["family"], "input family")
        partition = item["partition"]
        require(partition in ("census", "development", "evaluation"), "invalid partition")
        families.setdefault(family, set()).add(partition)
        require(
            not {"development", "evaluation"}.issubset(families[family]),
            f"development/evaluation family leakage: {family}",
        )
        check_file(root, item)
        hashes.setdefault(item["sha256"], set()).add(partition)
        require(
            not {"development", "evaluation"}.issubset(hashes[item["sha256"]]),
            "identical input bytes leak across development and evaluation",
        )
        inputs[identity] = item
    require(
        isinstance(design["experiments"], list) and bool(design["experiments"]),
        "at least one experiment is required",
    )
    experiments = {}
    for experiment in design["experiments"]:
        fields(
            experiment,
            "id kind question primary_endpoint secondary_endpoints input_ids",
            "experiment",
        )
        identity = nonempty(experiment["id"], "experiment id")
        require(identity not in experiments, "duplicate experiment id")
        require(experiment["kind"] in ("census", "family_holdout"), "invalid experiment kind")
        nonempty(experiment["question"], "question")
        endpoint = fields(
            experiment["primary_endpoint"],
            "name definition analysis_unit decision_rule",
            "primary_endpoint",
        )
        for key, value in endpoint.items():
            nonempty(value, "primary_endpoint." + key)
        strings(experiment["secondary_endpoints"], "secondary_endpoints", allow_empty=True)
        ids = strings(experiment["input_ids"], "input_ids", allow_empty=status == "planned")
        require(set(ids).issubset(inputs), "unknown experiment input")
        if status != "planned" and experiment["kind"] == "family_holdout":
            partitions = {inputs[item]["partition"] for item in ids}
            require(
                {"development", "evaluation"}.issubset(partitions),
                "frozen family_holdout needs development and evaluation inputs",
            )
        experiments[identity] = experiment
    require(
        isinstance(contract["runs"], list) and isinstance(contract["claims"], list),
        "runs and claims must be lists",
    )
    frozen_at = None
    if status == "planned":
        require(
            contract["freeze"] is None and not contract["runs"],
            "planned contract cannot contain a freeze or runs",
        )
    else:
        require(not design["freeze_blockers"], "resolve freeze blockers before freezing")
        freeze = fields(
            contract["freeze"], "design_sha256 commit frozen_at decision_record", "freeze"
        )
        require(freeze["design_sha256"] == design_digest(design), "frozen design hash mismatch")
        hexadecimal(freeze["commit"], 40, "freeze commit")
        frozen_at = timestamp(freeze["frozen_at"])
        fields(freeze["decision_record"], "path sha256", "freeze decision_record")
        check_file(root, freeze["decision_record"])
        require(
            bool(contract["runs"]) == (status == "executed"),
            "executed status requires runs; frozen status precedes runs",
        )
    runs = {}
    for run in contract["runs"]:
        fields(
            run,
            "id experiment_id status design_sha256 implementation_commit started_at command exit_code artifacts",
            "run",
        )
        identity = nonempty(run["id"], "run id")
        require(identity not in runs, "duplicate run id")
        require(
            isinstance(run["experiment_id"], str) and run["experiment_id"] in experiments,
            "unknown run experiment",
        )
        require(run["status"] in ("completed", "failed"), "invalid run status")
        require(run["design_sha256"] == design_digest(design), "run design hash mismatch")
        hexadecimal(run["implementation_commit"], 40, "implementation commit")
        require(
            frozen_at is not None and timestamp(run["started_at"]) >= frozen_at,
            "run predates design freeze",
        )
        require(
            isinstance(run["command"], list) and bool(run["command"]),
            "command must be an argv list",
        )
        for argument in run["command"]:
            nonempty(argument, "command argument")
        require(
            type(run["exit_code"]) is int
            and (run["exit_code"] == 0) == (run["status"] == "completed"),
            "run status and exit code disagree",
        )
        require(isinstance(run["artifacts"], list), "run artifacts must be a list")
        roles = set()
        for artifact in run["artifacts"]:
            fields(artifact, "role path sha256", "run artifact")
            require(artifact["role"] in ("log", "results", "environment"), "invalid artifact role")
            roles.add(artifact["role"])
            check_file(root, artifact)
        require(
            "log" in roles and (run["status"] != "completed" or "results" in roles),
            "run needs a log and completed run needs results",
        )
        runs[identity] = run
    claim_ids, observed = set(), 0
    for claim in contract["claims"]:
        fields(claim, "id status text run_ids review limitations", "claim")
        identity = nonempty(claim["id"], "claim id")
        require(identity not in claim_ids, "duplicate claim id")
        claim_ids.add(identity)
        require(claim["status"] in ("planned", "held", "observed"), "invalid claim status")
        nonempty(claim["text"], "claim text")
        ids = strings(claim["run_ids"], "claim run_ids", allow_empty=claim["status"] != "observed")
        require(set(ids).issubset(runs), "claim references unknown run")
        strings(claim["limitations"], "claim limitations")
        if claim["review"] is not None:
            fields(claim["review"], "path sha256", "claim review")
            check_file(root, claim["review"])
        if claim["status"] == "observed":
            require(
                all(runs[item]["status"] == "completed" for item in ids)
                and claim["review"] is not None,
                "observed claim needs completed evidence and review",
            )
            observed += 1
    return {
        "status": status,
        "experiments": len(experiments),
        "runs": len(runs),
        "observed_claims": observed,
        "design_sha256": design_digest(design),
        "scientific_acceptance": False,
        "boundary": "Integrity only; no proof of authenticity, scientific truth, rights or acceptance.",
    }


def previous_contracts(root: Path, revision: str) -> dict:
    hexadecimal(revision, 40, "baseline revision")

    def git(*arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        require(result.returncode == 0, "publication baseline unavailable")
        return result.stdout

    git("cat-file", "-e", revision + "^{commit}")
    paths = git("ls-tree", "-r", "--name-only", "-z", revision, "--", str(CONTRACTS)).split("\0")
    previous = {}
    for name in paths:
        path = Path(name)
        if path.parent == CONTRACTS and path.suffix == ".json":
            raw = git("show", revision + ":" + name)
            require(len(raw.encode("utf-8")) <= 10_000_000, "baseline contract exceeds size limit")
            previous[name] = json.loads(raw)
    return previous


def preserve_history(previous: dict, current: dict, path: str) -> None:
    fields(previous, "schema_version status design freeze runs claims", "baseline contract")
    require(
        previous["schema_version"] == current["schema_version"]
        and previous["status"] in ("planned", "frozen", "executed"),
        "invalid baseline contract",
    )
    if previous["status"] in ("frozen", "executed"):
        require(
            current["design"] == previous["design"] and current["freeze"] == previous["freeze"],
            f"{path}: frozen design and freeze are immutable; retain this file and add a versioned amendment",
        )
    require(
        isinstance(previous["runs"], list) and isinstance(previous["claims"], list),
        "invalid baseline runs or claims",
    )
    runs = {run["id"]: run for run in current["runs"]}
    for run in previous["runs"]:
        require(
            isinstance(run, dict) and runs.get(run.get("id")) == run,
            f"{path}: existing runs, including failures, must be retained unchanged",
        )
    claims = {claim["id"]: claim for claim in current["claims"]}
    for claim in previous["claims"]:
        require(
            isinstance(claim, dict) and claim.get("id") in claims,
            f"{path}: existing claim IDs must be retained",
        )
        if claim.get("status") == "observed":
            require(
                claim == claims[claim["id"]],
                f"{path}: observed claims are immutable; record corrections in a versioned amendment",
            )


def validate_contracts(
    root: Path = ROOT, baseline_revision: str | None = None, contract_path: Path | None = None
) -> dict:
    root = root.resolve()
    previous = previous_contracts(root, baseline_revision) if baseline_revision is not None else {}
    paths = (
        set((root / CONTRACTS).glob("*.json"))
        if contract_path is None
        else {contract_path if contract_path.is_absolute() else root / contract_path}
    )
    # A targeted check cannot hide deletion or rewriting of another published contract.
    for name in previous:
        path = root / name
        require(path.is_file(), f"published contract must be retained: {name}")
        paths.add(path)
    require(bool(paths), "no publication contracts found")
    results = {}
    for path in sorted(paths):
        require(
            path.resolve().is_relative_to(root) and path.is_file(),
            "contract absent or outside repository root",
        )
        require(path.stat().st_size <= 10_000_000, "contract exceeds size limit")
        contract = json.loads(path.read_text(encoding="utf-8"))
        name = path.relative_to(root).as_posix()
        results[name] = validate(contract, root)
        if name in previous:
            preserve_history(previous[name], contract, name)
    return {
        "contracts": results,
        "baseline_revision": baseline_revision,
        "history_checked": baseline_revision is not None,
        "scientific_acceptance": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        help="Check one contract; defaults to every contracts/publication/*.json",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--baseline-revision",
        help="Exact trusted base commit; retain earlier freezes, runs and claims",
    )
    args = parser.parse_args(argv)
    try:
        result = validate_contracts(args.root, args.baseline_revision, args.contract)
    except (
        OSError,
        UnicodeError,
        ValueError,
        TypeError,
        KeyError,
        subprocess.SubprocessError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
