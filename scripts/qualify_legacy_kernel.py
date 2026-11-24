#!/usr/bin/env python3
"""Execute the frozen notebooks through real kernels and compare the two receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from collections import Counter
from importlib import metadata
from pathlib import Path

from scripts import verify_legacy_standardflow as legacy

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ("6.25.0", "6.31.0")
PROTOCOL_CHECKS = (
    "kernel_info",
    "completion",
    "inspection",
    "error_and_recovery",
    "interrupt_and_recovery",
    "restart_and_state_reset",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def pins(path: Path) -> dict[str, str]:
    result = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([\w.-]+)==([\w.!+-]+)", line)
        if match is None or canonical(match[1]) in result:
            raise ValueError(f"Expected one exact, unique pin per line: {line}")
        result[canonical(match[1])] = match[2]
    return result


def outputs(messages: list[dict]) -> list[dict]:
    """Keep visible content; protocol IDs/counts and stream chunk boundaries are transport data."""
    result = []
    for message in messages:
        kind, content = message["msg_type"], message["content"]
        if kind == "stream":
            if result and result[-1].get("name") == content["name"]:
                result[-1]["text"] += content["text"]
            else:
                result.append({"type": kind, "name": content["name"], "text": content["text"]})
        elif kind in ("display_data", "execute_result"):
            result.append(
                {"type": kind, "data": content["data"], "metadata": content.get("metadata", {})}
            )
    return result


def execute(client, code: str, *, status: str = "ok", hook=None) -> tuple[list[dict], dict]:
    messages = []

    def collect(message):
        messages.append(message)
        if hook is not None:
            hook(message)

    reply = client.execute_interactive(
        code,
        timeout=45,
        allow_stdin=False,
        stop_on_error=True,
        output_hook=collect,
    )["content"]
    if reply.get("status") != status:
        raise RuntimeError(f"Unexpected kernel execution reply: {reply}")
    if status == "ok" and any(m["msg_type"] == "error" for m in messages):
        raise RuntimeError("Kernel emitted an error despite an ok execution reply")
    return outputs(messages), reply


def identity(client, version: str) -> dict:
    visible, _ = execute(
        client,
        "import sys, json, importlib.metadata\n"
        "print(json.dumps({'executable':sys.executable,'prefix':sys.prefix,"
        "'ipykernel':importlib.metadata.version('ipykernel')}))",
    )
    actual = json.loads("".join(item.get("text", "") for item in visible))
    if actual != {"executable": sys.executable, "prefix": sys.prefix, "ipykernel": version}:
        raise RuntimeError(f"Kernel interpreter/profile mismatch: {actual}")
    return actual


def shutdown(manager, client) -> None:
    reply = client.shutdown(reply=True, timeout=15)["content"]
    if reply.get("restart") is not False:
        raise RuntimeError("Kernel did not acknowledge the requested shutdown")
    if manager.provisioner.process.wait(timeout=15) != 0:
        raise RuntimeError("Kernel did not exit successfully after acknowledging shutdown")


def protocol_smoke(manager, client, version: str) -> dict:
    info = client.kernel_info(reply=True, timeout=15)["content"]
    if info["language_info"]["name"] != "python" or not info["protocol_version"].startswith("5."):
        raise RuntimeError("Unexpected kernel language/protocol")
    execute(client, "standardflow_probe_value = 42")
    completion = client.complete("standardflow_probe_", reply=True, timeout=15)["content"]
    inspection = client.inspect("standardflow_probe_value", reply=True, timeout=15)["content"]
    if completion["status"] != "ok" or "standardflow_probe_value" not in completion["matches"]:
        raise RuntimeError("Kernel completion lost the executed variable")
    if inspection["status"] != "ok" or not inspection["found"]:
        raise RuntimeError("Kernel inspection did not find the executed variable")
    _, error = execute(client, "raise ValueError('standardflow expected error')", status="error")
    if error.get("ename") != "ValueError" or error.get("evalue") != "standardflow expected error":
        raise RuntimeError("Kernel error reply lost its type or message")
    execute(client, "assert standardflow_probe_value == 42")

    interrupted = False

    def interrupt_when_ready(message):
        nonlocal interrupted
        if (
            not interrupted
            and message["msg_type"] == "stream"
            and "standardflow-interrupt-ready" in message["content"]["text"]
        ):
            interrupted = True
            manager.interrupt_kernel()

    _, error = execute(
        client,
        "import time\nprint('standardflow-interrupt-ready', flush=True)\ntime.sleep(60)",
        status="error",
        hook=interrupt_when_ready,
    )
    if not interrupted or error.get("ename") != "KeyboardInterrupt":
        raise RuntimeError("Kernel interrupt did not terminate the running cell")
    execute(client, "assert standardflow_probe_value == 42")
    manager.restart_kernel(now=False)
    client.wait_for_ready(timeout=30)
    identity(client, version)
    execute(client, "assert 'standardflow_probe_value' not in globals()")
    return {
        "kernel_info": True,
        "completion": True,
        "inspection": True,
        "error_and_recovery": True,
        "interrupt_and_recovery": True,
        "restart_and_state_reset": True,
        "protocol_version": info["protocol_version"],
    }


def qualify(version: str, evidence: Path) -> dict:
    import psutil
    from jupyter_client import KernelManager
    from jupyter_client.kernelspec import KernelSpecManager

    provenance = legacy.verify_history()
    host = ROOT / "requirements/legacy-standardflow.txt"
    extra = ROOT / "requirements/legacy-kernel-qualification.txt"
    host_pins, extra_pins = pins(host), pins(extra)
    if host_pins.keys() & extra_pins.keys() or "ipykernel" in host_pins | extra_pins:
        raise ValueError("Kernel-only pins must not replace any maintained host pin")
    expected = host_pins | extra_pins | {"ipykernel": version}
    installed = {
        canonical(d.metadata["Name"]): d.version
        for d in metadata.distributions()
        if canonical(d.metadata["Name"]) != "pip"
    }
    if len(expected) != 42 or installed != expected:
        raise RuntimeError(f"Expected the exact 42-package comparison profile; got {installed}")
    legacy.run([sys.executable, "-m", "pip", "check"], ROOT)
    receipt = {
        "result": "pass",
        "ipykernel": version,
        "python": sys.version.split()[0],
        "provenance": provenance,
        "dependencies": installed,
        "host_profile_sha256": digest(host.read_bytes()),
        "kernel_profile_sha256": digest(extra.read_bytes()),
        "saved_notebook_outputs_used": False,
        "notebooks": [],
    }
    with tempfile.TemporaryDirectory(prefix="standardflow-real-kernel-") as directory:
        temporary = Path(directory)
        work = temporary / "application"
        receipt["application"] = legacy.exercise(ROOT / "legacy/standardflow", work)
        # Tests/reference bytes must not supply outputs for the real-kernel observation.
        images = work / "examples/images"
        shutil.rmtree(images, ignore_errors=True)
        images.mkdir()
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PYTHONNOUSERSITE"] = "1"
        for variable in (
            "JUPYTER_RUNTIME_DIR",
            "JUPYTER_CONFIG_DIR",
            "JUPYTER_DATA_DIR",
            "IPYTHONDIR",
        ):
            target = temporary / variable.lower()
            target.mkdir()
            environment[variable] = str(target)
        spec = temporary / "kernels/standardflow"
        spec.mkdir(parents=True)
        (spec / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [
                        sys.executable,
                        "-Xfrozen_modules=off",
                        "-m",
                        "ipykernel_launcher",
                        "-f",
                        "{connection_file}",
                        "--HistoryManager.hist_file=:memory:",
                    ],
                    "display_name": "StandardFlow qualification",
                    "language": "python",
                }
            )
        )
        specs = KernelSpecManager(kernel_dirs=[str(spec.parent)], ensure_native_kernel=False)
        notebooks = sorted((work / "examples/notebooks").glob("*.ipynb"))
        if len(notebooks) != 11:
            raise RuntimeError("Expected all 11 frozen notebook fixtures")
        for index, notebook in enumerate(notebooks):
            cells = [
                "".join(c["source"])
                for c in json.loads(notebook.read_text())["cells"]
                if c["cell_type"] == "code"
            ]
            manager = KernelManager(
                kernel_name="standardflow",
                kernel_spec_manager=specs,
                ip="127.0.0.1",
                transport="tcp",
            )
            client, pid = None, None
            with (evidence / f"{notebook.stem}.log").open("w") as log:
                try:
                    manager.start_kernel(
                        cwd=str(notebook.parent), env=environment, stdout=log, stderr=log
                    )
                    pid = manager.provisioner.pid
                    client = manager.blocking_client()
                    client.start_channels()
                    client.wait_for_ready(timeout=30)
                    connection = manager.get_connection_info()
                    if connection["ip"] != "127.0.0.1" or connection["transport"] != "tcp":
                        raise RuntimeError("Kernel is not bound to TCP loopback")
                    receipt["kernel_identity"] = identity(client, version)
                    if index == 0:
                        receipt["protocol"] = protocol_smoke(manager, client, version)
                        pid = manager.provisioner.pid
                    visible = [execute(client, code)[0] for code in cells]
                    mime = Counter(
                        m for cell in visible for item in cell for m in item.get("data", {})
                    )
                    shutdown(manager, client)
                    receipt["notebooks"].append(
                        {
                            "name": notebook.name,
                            "source_sha256": digest(notebook.read_bytes()),
                            "code_cells": len(cells),
                            "mime_counts": dict(sorted(mime.items())),
                            "shutdown_reply_observed": True,
                            "visible_output_sha256": digest(
                                json.dumps(visible, sort_keys=True).encode()
                            ),
                        }
                    )
                finally:
                    if manager.has_kernel:
                        manager.shutdown_kernel(now=True)
                    if client is not None:
                        client.stop_channels()
                    if manager.is_alive() or (pid is not None and psutil.pid_exists(pid)):
                        raise RuntimeError("Kernel process survived cleanup")
            print(f"ipykernel {version}: {notebook.name}: {len(cells)} cells passed", flush=True)
        if sum(n["code_cells"] for n in receipt["notebooks"]) != 43:
            raise RuntimeError("Expected execution of all 43 original code cells")
        files = sorted(images.glob("*.png"))
        if len(files) != 6 or any(
            not p.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for p in files
        ):
            raise RuntimeError("Real notebooks did not create all six valid PNG outputs")
        receipt["rendered_images"] = {p.name: digest(p.read_bytes()) for p in files}
        receipt["clean_shutdowns"] = len(notebooks)
    if legacy.verify_history() != provenance:
        raise RuntimeError("Import provenance changed during kernel qualification")
    return receipt


def compare(baseline: dict, candidate: dict) -> dict:
    for receipt, version in zip((baseline, candidate), VERSIONS, strict=True):
        if receipt.get("result") != "pass" or receipt.get("ipykernel") != version:
            raise ValueError(
                "Comparison needs two successful, correctly identified kernel receipts"
            )
        if receipt.get("dependencies", {}).get("ipykernel") != version:
            raise ValueError("The installed kernel version disagrees with the receipt identity")
        if (
            len(receipt.get("notebooks", [])) != 11
            or sum(n["code_cells"] for n in receipt["notebooks"]) != 43
            or receipt.get("clean_shutdowns") != 11
            or len(receipt.get("rendered_images", {})) != 6
            or not all(n.get("shutdown_reply_observed") is True for n in receipt["notebooks"])
            or receipt.get("saved_notebook_outputs_used") is not False
            or receipt.get("application", {}).get("tests") != 52
            or len(receipt.get("application", {}).get("files", {})) != 21
            or any(receipt.get("protocol", {}).get(k) is not True for k in PROTOCOL_CHECKS)
        ):
            raise ValueError("A receipt lacks complete notebook execution/output/cleanup evidence")
    before = {k: v for k, v in baseline["dependencies"].items() if k != "ipykernel"}
    after = {k: v for k, v in candidate["dependencies"].items() if k != "ipykernel"}
    if len(before) != 41 or before != after:
        raise ValueError("The environments differ beyond the compared ipykernel version")
    for key in (
        "python",
        "provenance",
        "host_profile_sha256",
        "kernel_profile_sha256",
        "application",
        "protocol",
        "notebooks",
        "rendered_images",
    ):
        if baseline[key] != candidate[key]:
            raise ValueError(f"Kernel compatibility differs: {key}")
    return {
        "result": "pass",
        "versions": list(VERSIONS),
        "notebooks_per_version": 11,
        "code_cells_per_version": 43,
        "identical_pngs": 6,
        "identical_cli_files": len(baseline["application"]["files"]),
        "unchanged_other_packages": len(before),
        "protocol": baseline["protocol"],
        "claim": "frozen notebook and tested Jupyter protocol compatibility",
        "limits": [
            "not a notebook GUI/browser qualification",
            "not general notebook support",
            "not Rust parity, methodological validation, rights or offline-security acceptance",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--expected-version", choices=VERSIONS)
    mode.add_argument("--compare", nargs=2, type=Path, metavar=("BASELINE", "CANDIDATE"))
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        if arguments.compare:
            receipt = compare(*(json.loads(p.read_text()) for p in arguments.compare))
        else:
            receipt = qualify(arguments.expected_version, arguments.output.parent)
    except Exception as error:
        receipt = {
            "result": "fail",
            "error": f"{type(error).__name__}: {error}",
            "ipykernel": arguments.expected_version,
        }
    arguments.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
