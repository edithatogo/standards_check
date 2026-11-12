import pytest
from unittest.mock import patch, MagicMock
from extract_and_convert import extract_text_from_docx
import extract_and_convert

def test_extract_text_from_docx_success():
    # Setup mock docx.Document
    mock_doc = MagicMock()
    mock_doc.paragraphs = [
        MagicMock(text="Paragraph 1"),
        MagicMock(text="Paragraph 2")
    ]

    # We patch the object imported by the module, or the module itself if docx is not a package
    with patch.object(extract_and_convert, 'docx') as mock_docx:
        mock_docx.Document.return_value = mock_doc
        result = extract_text_from_docx("dummy.docx")
        assert result == "Paragraph 1\nParagraph 2"

def test_extract_text_from_docx_exception():
    with patch.object(extract_and_convert, 'docx') as mock_docx:
        mock_docx.Document.side_effect = Exception("Test error")
        result = extract_text_from_docx("dummy.docx")
        assert result is None
