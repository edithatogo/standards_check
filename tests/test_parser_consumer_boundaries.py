"""Security-sensitive XML consumers and pinned helper loading fail before use."""

import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scripts import ecoevo_pdf_grid, generate_sbom, qualify_legacy_prisma, validate_artifacts

ENTITY_XML = b'<!DOCTYPE svg [<!ENTITY injected "untrusted content">]><svg>&injected;</svg>'


def test_generated_svg_validation_rejects_entity_declarations(tmp_path, monkeypatch, capsys):
    path = tmp_path / "injected.svg"
    path.write_bytes(ENTITY_XML)
    monkeypatch.setattr(validate_artifacts, "ROOT", tmp_path)
    with pytest.raises(SystemExit) as error:
        validate_artifacts.validate_svg(path, {})
    assert error.value.code == 1
    assert "not valid SVG XML" in capsys.readouterr().err


def test_legacy_svg_count_comparison_rejects_entity_declarations(tmp_path):
    path = tmp_path / "injected.svg"
    path.write_bytes(ENTITY_XML)
    with pytest.raises(ValueError):
        qualify_legacy_prisma.legacy_svg_counts(path)


def test_poppler_xml_is_checked_before_rasterization(monkeypatch):
    process = Mock(return_value=subprocess.CompletedProcess([], 0, ENTITY_XML, b""))
    monkeypatch.setattr(ecoevo_pdf_grid.subprocess, "run", process)
    with pytest.raises(ValueError):
        ecoevo_pdf_grid.extract_poppler(b"%PDF synthetic input")
    assert process.call_count == 1
    assert process.call_args.args[0][0] == "pdftotext"


@pytest.mark.parametrize("spec", [None, SimpleNamespace(loader=None)])
def test_unloadable_pinned_helper_cannot_execute(tmp_path, monkeypatch, spec):
    directory = tmp_path / "scripts"
    directory.mkdir()
    helper = directory / "helper.py"
    helper.write_text("raise RuntimeError('must not execute')\n")
    monkeypatch.setattr(
        generate_sbom.subprocess, "check_output", lambda *args, **kwargs: helper.read_bytes()
    )
    monkeypatch.setattr(generate_sbom.importlib.util, "spec_from_file_location", lambda *args: spec)
    with pytest.raises(ValueError, match="cannot be loaded"):
        generate_sbom.central_helper(tmp_path, "helper.py")
