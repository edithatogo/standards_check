"""Synthetic protocol faults test receipt gating; these are not real-kernel qualification."""

import json
import sys
from unittest.mock import Mock

from hypothesis import given, settings, strategies as st
import pytest

from scripts import qualify_legacy_kernel as kernel


@pytest.mark.parametrize(
    "pins",
    ["package>=1.0", "package", "package==1.0\npackage==2.0", "My.Package==1\nmy_package==2"],
)
def test_profile_rejects_mutable_or_ambiguous_pins(tmp_path, pins):
    path = tmp_path / "profile.txt"
    path.write_text(pins)
    with pytest.raises(ValueError, match="exact, unique"):
        kernel.pins(path)


def test_profile_canonicalization_retains_only_exact_unique_pins(tmp_path):
    path = tmp_path / "profile.txt"
    path.write_text("# comment\n\nMy_Package==1.2.3\nOther.Package==2.0rc1\n")
    assert kernel.pins(path) == {"my-package": "1.2.3", "other-package": "2.0rc1"}


@settings(max_examples=64, derandomize=True)
@given(chunks=st.lists(st.text(max_size=40), min_size=1, max_size=20))
def test_visible_output_hash_is_invariant_to_stdout_chunking(chunks):
    split = [{"msg_type": "stream", "content": {"name": "stdout", "text": text}} for text in chunks]
    joined = [{"msg_type": "stream", "content": {"name": "stdout", "text": "".join(chunks)}}]
    # Invisible protocol traffic cannot create output evidence.
    split.append({"msg_type": "status", "content": {"execution_state": "idle"}})
    assert kernel.outputs(split) == kernel.outputs(joined)
    assert kernel.digest(json.dumps(kernel.outputs(split)).encode()) == kernel.digest(
        json.dumps(kernel.outputs(joined)).encode()
    )


def client_for_identity(identity):
    client = Mock()

    def execute(code, **kwargs):
        kwargs["output_hook"](
            {"msg_type": "stream", "content": {"name": "stdout", "text": json.dumps(identity)}}
        )
        return {"content": {"status": "ok"}}

    client.execute_interactive.side_effect = execute
    return client


def test_identity_binds_interpreter_prefix_and_kernel_version():
    actual = {"executable": sys.executable, "prefix": sys.prefix, "ipykernel": "6.31.0"}
    assert kernel.identity(client_for_identity(actual), "6.31.0") == actual
    for field in actual:
        invalid = actual | {field: "another profile"}
        with pytest.raises(RuntimeError, match="interpreter/profile mismatch"):
            kernel.identity(client_for_identity(invalid), "6.31.0")


def protocol_client(defect=None):
    client, manager = Mock(), Mock()
    info = {"language_info": {"name": "python"}, "protocol_version": "5.3"}
    if defect == "language":
        info["language_info"]["name"] = "other"
    client.kernel_info.return_value = {"content": info}
    client.complete.return_value = {
        "content": {
            "status": "ok",
            "matches": [] if defect == "completion" else ["standardflow_probe_value"],
        }
    }
    client.inspect.return_value = {"content": {"status": "ok", "found": defect != "inspection"}}

    def execute(code, **kwargs):
        content = {"status": "ok"}
        if code.startswith("raise ValueError"):
            content = {
                "status": "error",
                "ename": "ValueError",
                "evalue": "wrong" if defect == "error" else "standardflow expected error",
            }
        elif "time.sleep" in code:
            if defect != "interrupt":
                message = {
                    "msg_type": "stream",
                    "content": {"name": "stdout", "text": "standardflow-interrupt-ready"},
                }
                kwargs["output_hook"](message)
                kwargs["output_hook"](message)
            content = {"status": "error", "ename": "KeyboardInterrupt"}
        elif "importlib.metadata" in code:
            identity = {"executable": sys.executable, "prefix": sys.prefix, "ipykernel": "6.31.0"}
            kwargs["output_hook"](
                {"msg_type": "stream", "content": {"name": "stdout", "text": json.dumps(identity)}}
            )
        return {"content": content}

    client.execute_interactive.side_effect = execute
    return manager, client


@pytest.mark.parametrize(
    "defect, message",
    [
        ("language", "language/protocol"),
        ("completion", "completion"),
        ("inspection", "inspection"),
        ("error", "type or message"),
        ("interrupt", "interrupt"),
    ],
)
def test_protocol_cannot_report_success_after_a_failed_exchange(defect, message):
    manager, client = protocol_client(defect)
    with pytest.raises(RuntimeError, match=message):
        kernel.protocol_smoke(manager, client, "6.31.0")
    manager.restart_kernel.assert_not_called()


def test_protocol_interrupt_is_single_shot_and_restart_requires_identity():
    manager, client = protocol_client()
    result = kernel.protocol_smoke(manager, client, "6.31.0")
    assert all(result[name] is True for name in kernel.PROTOCOL_CHECKS)
    manager.interrupt_kernel.assert_called_once_with()
    manager.restart_kernel.assert_called_once_with(now=False)
    client.wait_for_ready.assert_called_once_with(timeout=30)
    commands = [call.args[0] for call in client.execute_interactive.call_args_list]
    assert commands[-1] == "assert 'standardflow_probe_value' not in globals()"


def test_compare_cli_reports_invalid_evidence_as_failed(tmp_path, monkeypatch):
    baseline, candidate, output = (
        tmp_path / name for name in ("baseline.json", "candidate.json", "receipt.json")
    )
    baseline.write_text("{}")
    candidate.write_text("{}")
    monkeypatch.setattr(
        sys,
        "argv",
        ["qualify", "--compare", str(baseline), str(candidate), "--output", str(output)],
    )
    assert kernel.main() == 1
    receipt = json.loads(output.read_text())
    assert receipt["result"] == "fail"
    assert "successful, correctly identified" in receipt["error"]
