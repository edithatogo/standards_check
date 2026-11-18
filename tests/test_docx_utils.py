"""Preserve the distinct strict CLI and tolerant batch extraction contracts."""

import importlib
from pathlib import Path
import subprocess
import sys

import docx
import pytest
from docx.opc.exceptions import PackageNotFoundError

from utils.docx_utils import extract_text_from_docx


@pytest.mark.parametrize(
    "module_name",
    ["extract_all_docx", "extract_and_convert", "extract_docx_content", "extract_docx"],
)
def test_docx_adapters_preserve_paragraph_order(module_name, tmp_path):
    path = tmp_path / "paragraphs.docx"
    document = docx.Document()
    document.add_paragraph("First paragraph")
    document.add_paragraph("")
    document.add_paragraph("Final paragraph")
    document.save(path)

    adapter = importlib.import_module(module_name)
    assert adapter.extract_text_from_docx(path) == "First paragraph\n\nFinal paragraph"


def test_shared_docx_reader_propagates_missing_file(tmp_path):
    with pytest.raises(PackageNotFoundError):
        extract_text_from_docx(str(tmp_path / "missing.docx"))


def test_cli_docx_reader_propagates_missing_file(tmp_path):
    import extract_docx

    with pytest.raises(PackageNotFoundError):
        extract_docx.extract_text_from_docx(str(tmp_path / "missing.docx"))


@pytest.mark.parametrize(
    "module_name", ["extract_all_docx", "extract_and_convert", "extract_docx_content"]
)
def test_batch_docx_adapters_report_missing_file(module_name, tmp_path, capsys):
    path = tmp_path / "missing.docx"
    adapter = importlib.import_module(module_name)

    assert adapter.extract_text_from_docx(path) is None
    assert f"Error extracting text from {path}:" in capsys.readouterr().out


def test_missing_docx_cli_returns_failure(tmp_path):
    script = Path(__file__).resolve().parents[1] / "extract_docx.py"
    path = tmp_path / "missing.docx"

    result = subprocess.run(
        [sys.executable, str(script), str(path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"Error extracting text from {path}:" in result.stdout
    assert "\nNone\n" not in result.stdout
