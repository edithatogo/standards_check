#!/usr/bin/env python3
"""Inventory one maintained dependency profile, with checkout-bound evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
POLICY_REVISION = "a3cc8dccdb67e6f122c71cec713194cdec792d07"
PYTHON_PROFILES = {
    "foundation": ("standardflow-foundation", (3, 14), True),
    "legacy": ("legacy-standardflow", (3, 12), True),
    "tests": ("python-tests", (3, 12), False),
    "assurance": ("assurance-tools", (3, 12), True),
    "kernel-baseline": ("legacy-kernel-qualification", (3, 12), True),
    "kernel-candidate": ("legacy-kernel-qualification", (3, 12), True),
}
COMPONENTS = ("rust", "node", "api", *(f"python-{key}" for key in PYTHON_PROFILES))


def run(command: list[str], *, cwd: Path = ROOT, output: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True,
                            timeout=900, env={key: value for key, value in os.environ.items()
                                              if not key.startswith("SYFT_")})
    if output is not None:
        output.write_text(result.stdout, encoding="utf-8")
    return result.stdout.strip()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def central_helper(policy: Path, filename: str):
    path = policy / "scripts" / filename
    expected = subprocess.check_output(["git", "show", f"{POLICY_REVISION}:scripts/{filename}"], cwd=policy)
    if path.read_bytes() != expected:
        raise ValueError(f"central helper differs from pinned policy revision: {filename}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_inputs(component: str) -> list[Path]:
    if component == "rust":
        return [ROOT / "Cargo.lock", ROOT / "Cargo.toml", *sorted((ROOT / "crates").glob("*/Cargo.toml"))]
    if component in ("node", "api"):
        base = ROOT if component == "node" else ROOT / "api"
        return [base / "package.json", base / "package-lock.json"]
    profile, _, _ = PYTHON_PROFILES[component.removeprefix("python-")]
    if component.startswith("python-kernel-"):
        return [ROOT / "requirements/legacy-standardflow.txt", ROOT / "requirements" / f"{profile}.txt",
                ROOT / ".github/workflows/standardflow-legacy.yml"]
    return [ROOT / "requirements" / f"{profile}.txt"]


def package_id(name: str, version: str, ecosystem: str) -> tuple[str, str]:
    return (re.sub(r"[-_.]+", "-", name).lower() if ecosystem == "pypi" else name, version)


def verify_inventory(document: dict, expected: set[tuple[str, str]], ecosystem: str) -> None:
    if not isinstance(document, dict):
        raise ValueError("inventory must be a JSON object")
    components = document.get("components")
    if not isinstance(components, list):
        raise ValueError("inventory components must be an array")
    actual = set()
    for package in components:
        if (not isinstance(package, dict)
                or any(not isinstance(package.get(key), str) or not package[key] for key in ("name", "version", "purl"))
                or not package["purl"].startswith(f"pkg:{ecosystem}/")):
            raise ValueError(f"inventory must contain only identifiable {ecosystem} components")
        purl = package["purl"]
        name, version = unquote(purl.split("?", 1)[0].split("#", 1)[0]).split("/", 1)[1].rsplit("@", 1)
        actual.add(package_id(name, version, ecosystem))
    if not expected or actual != expected:
        raise ValueError(f"inventory mismatch: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")


def python_inventory(component: str, output: Path, temporary: Path, policy: Path, receipt: dict) -> dict:
    _, required_python, closed = PYTHON_PROFILES[component.removeprefix("python-")]
    if sys.version_info[:2] != required_python:
        raise ValueError(f"{component} requires Python {required_python[0]}.{required_python[1]}")
    requirements = [path for path in source_inputs(component) if path.suffix == ".txt"]
    pins = set()
    lines = [line for path in requirements for line in path.read_text(encoding="utf-8").splitlines()]
    extra_packages = []
    if component.startswith("python-kernel-"):
        # The existing two-version qualification loop owns these pins. Fail on source-site drift.
        workflow = (ROOT / ".github/workflows/standardflow-legacy.yml").read_text(encoding="utf-8")
        matches = re.findall(r"^\s*for kernel_version in ([0-9. ]+); do$", workflow, re.MULTILINE)
        versions = matches[0].split() if len(matches) == 1 else []
        if len(versions) != 2 or any(not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value) for value in versions):
            raise ValueError("expected the exact two-version kernel qualification loop")
        receipt["kernel_version"] = versions[0 if component.endswith("baseline") else 1]
        extra_packages = [f"ipykernel=={receipt['kernel_version']}"]
        lines.extend(extra_packages)
    for line in lines:
        line = line.partition("#")[0].strip()
        if line:
            # ponytail: only this Python-version marker is needed; extend when profiles require more.
            match = re.fullmatch(
                r"""([A-Za-z0-9_.-]+)==([A-Za-z0-9.!+-]+)(?:\s*;\s*python_version\s*<\s*(["'])([0-9]+)\.([0-9]+)\3)?""",
                line,
            )
            if match is None:
                raise ValueError(f"expected exact dependency pin with a supported marker: {line}")
            if match[3] is None or sys.version_info[:2] < (int(match[4]), int(match[5])):
                pins.add(package_id(match[1], match[2], "pypi"))
    environment = temporary / "environment"
    run([sys.executable, "-m", "venv", str(environment)])
    python = environment / "bin" / "python"
    pip = [str(python), "-m", "pip", "--disable-pip-version-check", "--no-input"]
    install = [*pip, "install", "--report", str(output / "install.json"),
               *(argument for path in requirements for argument in ("-r", str(path))), *extra_packages]
    run([*install, *(["--no-deps"] if closed else [])], output=output / "install.log")
    run([*pip, "check"], output=output / "pip-check.log")
    inspected = json.loads(run([*pip, "inspect", "--local"], output=output / "environment.json"))
    expected = {package_id(item["metadata"]["name"], item["metadata"]["version"], "pypi")
                for item in inspected["installed"]}
    if not pins <= expected or (closed and {name for name, _ in expected - pins} - {"pip"}):
        raise ValueError("installed environment differs from the declared dependency profile")
    scanner = central_helper(policy, "grype_scan.py")
    syft, receipt["syft"] = scanner.download_tool("syft", temporary)
    version = json.loads(run([str(syft), "version", "-o", "json"], output=output / "syft-version.json"))
    if version["version"].lstrip("v") != receipt["syft"]["version"]:
        raise ValueError("Syft binary version differs from its verified release archive")
    config = temporary / "syft.yaml"
    config.write_text("check-for-app-update: false\n", encoding="utf-8")
    document = json.loads(run([
        str(syft), "scan", f"dir:{environment}", "--config", str(config),
        "--override-default-catalogers", "python-installed-package-cataloger", "--select-catalogers=-file",
        "--source-name", f"standards_check/{component}", "--source-version", receipt["source_commit"],
        "-o", "cyclonedx-json",
    ]))
    verify_inventory(document, expected, "pypi")
    receipt.update(python=platform.python_version(), installed_distributions=len(expected),
                   resolution="exact profile closure plus bootstrap pip" if closed else "observed transitive resolution; not a source lock",
                   scope="isolated installed Python distributions and their metadata; includes bootstrap pip")
    return document


def generate(component: str, output: Path, temporary: Path, policy: Path, receipt: dict) -> dict:
    if component == "rust":
        receipt["scope"] = "all Cargo.lock packages, including build/dev/optional/target resolution; not linked binary composition"
        return central_helper(policy, "cargo_lock_sbom.py").generate(
            (ROOT / "Cargo.lock").read_bytes(), "standards_check/rust", receipt["source_commit"])
    if component.startswith("python-"):
        return python_inventory(component, output, temporary, policy, receipt)
    directory = ROOT if component == "node" else ROOT / "api"
    document = json.loads(run(["npm", "sbom", "--package-lock-only", "--sbom-format", "cyclonedx",
                               "--include=dev", "--include=optional", "--include=peer", "--ignore-scripts"], cwd=directory))
    lock = json.loads((directory / "package-lock.json").read_text(encoding="utf-8"))
    expected = {(package.get("name", path.rsplit("node_modules/", 1)[-1]), package["version"])
                for path, package in lock["packages"].items() if path}
    verify_inventory(document, expected, "npm")
    receipt.update(node=run(["node", "--version"]), npm=run(["npm", "--version"]),
                   locked_package_records=len(lock["packages"]) - 1,
                   scope="all package-lock resolved identities, including dev/optional/peer; not installed or bundled composition")
    return document


def collect(component: str, output: Path, policy: Path, allow_dirty: bool = False) -> dict:
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError("output must be a new or empty regular directory")
    output.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "outcome": "error", "component": component,
               "policy_revision": POLICY_REVISION, "generator_sha256": digest(Path(__file__).read_bytes()),
               "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "claim_boundary": "dependency inventory; excludes OS packages, interpreter/toolchain binaries, vendored native libraries, build downloads and released artifacts"}
    try:
        receipt["source_commit"] = run(["git", "rev-parse", "HEAD"])
        inputs = {str(path.relative_to(ROOT)): path.read_bytes() for path in source_inputs(component)}
        receipt["inputs_sha256"] = {path: digest(data) for path, data in inputs.items()}
        modified = [path for path, data in inputs.items()
                    if subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT) != data]
        receipt["modified_inputs"] = modified
        if modified and not allow_dirty:
            raise ValueError(f"dependency inputs differ from source commit: {modified}")
        with tempfile.TemporaryDirectory(prefix="standards-sbom-") as directory:
            document = generate(component, output, Path(directory), policy, receipt)
        summary = central_helper(policy, "grype_scan.py").inventory_summary(document)
        if any((ROOT / path).read_bytes() != data for path, data in inputs.items()):
            raise ValueError("dependency inputs changed during inventory generation")
        properties = document.setdefault("metadata", {}).setdefault("properties", [])
        properties.extend([
            {"name": "standards-check:source-commit", "value": receipt["source_commit"]},
            {"name": "standards-check:modified-inputs", "value": json.dumps(modified)},
            {"name": "standards-check:inputs-sha256", "value": json.dumps(receipt["inputs_sha256"], sort_keys=True)},
        ])
        write_json(output / "bom.cdx.json", document)
        receipt.update(summary, outcome="success", bom_sha256=digest((output / "bom.cdx.json").read_bytes()))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        receipt["error"] = str(error)
        if isinstance(error, subprocess.CalledProcessError):
            (output / "error.log").write_text(f"{error.stdout or ''}\n{error.stderr or ''}", encoding="utf-8")
    receipt["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    write_json(output / "receipt.json", receipt)
    (output / "SHA256SUMS").write_text("".join(f"{digest(path.read_bytes())}  {path.name}\n"
                                              for path in sorted(output.iterdir()) if path.is_file()), encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=COMPONENTS, required=True)
    parser.add_argument("--policy-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-dirty-inputs", action="store_true", help="local qualification only; records modified inputs explicitly")
    args = parser.parse_args()
    try:
        receipt = collect(args.component, args.output.absolute(), args.policy_dir.resolve(), args.allow_dirty_inputs)
    except (OSError, ValueError) as error:
        print(f"SBOM setup failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["outcome"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
