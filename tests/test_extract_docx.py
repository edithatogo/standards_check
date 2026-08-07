import pytest
from unittest.mock import MagicMock
from extract_docx import extract_text_from_docx

def test_extract_text_from_docx_normal(mocker):
    # Setup mock document and paragraphs
    mock_doc = MagicMock()
    mock_para1 = MagicMock()
    mock_para1.text = "First paragraph."
    mock_para2 = MagicMock()
    mock_para2.text = "Second paragraph."
    mock_doc.paragraphs = [mock_para1, mock_para2]

    # Patch docx.Document
    mocker.patch('extract_docx.docx.Document', return_value=mock_doc)

    # Call the function
    result = extract_text_from_docx("dummy_path.docx")

    # Assert result
    assert result == "First paragraph.\nSecond paragraph."

def test_extract_text_from_docx_empty(mocker):
    # Setup mock document and paragraphs
    mock_doc = MagicMock()
    mock_doc.paragraphs = []

    # Patch docx.Document
    mocker.patch('extract_docx.docx.Document', return_value=mock_doc)

    # Call the function
    result = extract_text_from_docx("dummy_path.docx")

    # Assert result
    assert result == ""
