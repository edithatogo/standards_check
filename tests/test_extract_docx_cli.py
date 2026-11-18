"""Exercise DOCX CLI behavior without replacing extraction-function tests."""

import sys
from unittest.mock import MagicMock, patch

import pytest

import extract_docx


def test_extract_text_from_docx_success():
    document = MagicMock()
    document.paragraphs = [MagicMock(text="Paragraph 1"), MagicMock(text="Paragraph 2")]
    with patch("docx.Document", return_value=document) as open_document:
        assert extract_docx.extract_text_from_docx("dummy.docx") == "Paragraph 1\nParagraph 2"
    open_document.assert_called_once_with("dummy.docx")


def test_main_happy_path(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["extract_docx.py", "test.docx"])
    with patch("extract_docx.extract_text_from_docx", return_value="Mocked content") as extract:
        extract_docx.main()
    extract.assert_called_once_with("test.docx")
    assert capsys.readouterr().out == "Mocked content\n"


def test_main_missing_args(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["extract_docx.py"])
    with patch("extract_docx.extract_text_from_docx") as extract:
        with pytest.raises(SystemExit) as error:
            extract_docx.main()
    assert error.value.code == 1
    extract.assert_not_called()
    assert "Usage: python extract_docx.py <file_path>" in capsys.readouterr().out


def test_main_extraction_error(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["extract_docx.py", "test.docx"])
    with patch("extract_docx.extract_text_from_docx", side_effect=ValueError("mock error")) as extract:
        with pytest.raises(SystemExit) as error:
            extract_docx.main()
    assert error.value.code == 1
    extract.assert_called_once_with("test.docx")
    assert "Error extracting text from test.docx: mock error" in capsys.readouterr().out
