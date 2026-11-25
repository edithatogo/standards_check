"""Retained application checks and synthetic failure tests for the parity harness."""

from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
from unittest.mock import Mock

import pytest

from scripts import verify_legacy_standardflow as legacy


def test_retained_application_runs_all_tests_and_produces_the_bounded_manifest(tmp_path):
    result = legacy.exercise(legacy.ROOT / "legacy/standardflow", tmp_path / "application")
    assert result["tests"] == 52
    assert len(result["files"]) == 21
    assert result["invalid_prisma_fixture"]["output_created"] is False
    assert result["module_entrypoint_requires_pythonpath"] is False
    assert all(len(item["sha256"]) == 64 and item["bytes"] > 0 for item in result["files"].values())


def source_directories(root):
    source = root / "source"
    source.mkdir()
    for name in ("src", "schemas", "data", "tests", "web", "examples"):
        (source / name).mkdir()
    return source


@pytest.mark.parametrize(
    "summary", ["Ran 51 tests", "Ran 52 tests\nOK (skipped=1)", "No test summary"]
)
def test_partial_application_suite_cannot_create_a_parity_receipt(tmp_path, monkeypatch, summary):
    source = source_directories(tmp_path)
    monkeypatch.setattr(legacy, "run", lambda *args: summary)
    with pytest.raises(RuntimeError, match="all 52 pinned"):
        legacy.exercise(source, tmp_path / "work")


@pytest.mark.parametrize(
    "returncode, stderr, output_created",
    [
        (0, "'invalid_data' is not of type 'integer'", False),
        (1, "unrelated failure", False),
        (1, "'invalid_data' is not of type 'integer'", True),
    ],
)
def test_invalid_fixture_must_fail_for_the_right_reason_without_output(
    tmp_path, monkeypatch, returncode, stderr, output_created
):
    source = source_directories(tmp_path)
    monkeypatch.setattr(legacy, "run", lambda *args: "Ran 52 tests\nOK")

    def rejected(command, **kwargs):
        if output_created:
            Path(command[-1]).write_text("incorrectly accepted")
        return subprocess.CompletedProcess(command, returncode, "", stderr)

    monkeypatch.setattr(legacy.subprocess, "run", rejected)
    with pytest.raises(RuntimeError, match="invalid PRISMA|rejected PRISMA"):
        legacy.exercise(source, tmp_path / "work")


def test_subprocess_wrapper_reports_failure_status_and_both_output_streams(tmp_path):
    assert "stdout" in legacy.run([sys.executable, "-c", "print('stdout')"], tmp_path)
    with pytest.raises(RuntimeError, match=r"Command failed \(7\)") as error:
        legacy.run(
            [
                sys.executable,
                "-c",
                "import sys;print('stdout');print('stderr',file=sys.stderr);sys.exit(7)",
            ],
            tmp_path,
        )
    assert "stdout" in str(error.value)
    assert "stderr" in str(error.value)


def synthetic_main_environment(tmp_path, monkeypatch):
    """No application qualification is claimed by these orchestration unit tests."""
    (tmp_path / "requirements").mkdir()
    (tmp_path / "requirements/legacy-standardflow.txt").write_text("# fixture\npackage==1.0\n")
    provenance = {
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "import_prefix": "legacy/standardflow",
        "preserved_revisions": 2,
    }
    history = Mock(side_effect=[provenance, deepcopy(provenance)])
    monkeypatch.setattr(legacy, "ROOT", tmp_path)
    monkeypatch.setattr(legacy, "verify_history", history)
    monkeypatch.setattr(legacy, "run", lambda command, *args: "tool 1.0\n")
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w"):
        pass
    monkeypatch.setattr(
        legacy.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, archive.getvalue(), b""),
    )
    exercise = Mock(
        side_effect=[
            {"tests": 52, "files": {"fixture": "same"}},
            {"tests": 52, "files": {"fixture": "same"}},
        ]
    )
    monkeypatch.setattr(legacy, "exercise", exercise)
    monkeypatch.setattr(legacy.importlib.metadata, "version", lambda name: "1.0")
    return history, exercise, provenance


@pytest.mark.parametrize("write_receipt", [False, True])
def test_synthetic_orchestration_binds_both_executions_and_preserves_claim_limits(
    tmp_path, monkeypatch, capsys, write_receipt
):
    history, exercise, _ = synthetic_main_environment(tmp_path, monkeypatch)
    output = tmp_path / "evidence/receipt.json"
    monkeypatch.setattr(
        sys, "argv", ["verify"] + (["--output", str(output)] if write_receipt else [])
    )
    legacy.main()
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["source_tree"] == receipt["received_tree"] == "b" * 40
    assert "not scientific validation" in receipt["claim_limits"]
    assert history.call_count == exercise.call_count == 2
    if write_receipt:
        assert json.loads(output.read_text()) == receipt


@pytest.mark.parametrize("defect", ["changed_results", "provenance_drift"])
def test_synthetic_orchestration_never_publishes_a_mismatched_receipt(
    tmp_path, monkeypatch, defect
):
    history, exercise, provenance = synthetic_main_environment(tmp_path, monkeypatch)
    if defect == "changed_results":
        exercise.side_effect = [{"files": {"one": "before"}}, {"files": {"one": "after"}}]
    else:
        history.side_effect = [provenance, provenance | {"source_tree": "c" * 40}]
    output = tmp_path / "receipt.json"
    monkeypatch.setattr(sys, "argv", ["verify", "--output", str(output)])
    with pytest.raises(RuntimeError, match="differ|changed"):
        legacy.main()
    assert not output.exists()
