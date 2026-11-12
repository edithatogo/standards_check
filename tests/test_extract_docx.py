import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import extract_docx
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import extract_docx

def test_extract_text_from_docx_success(tmp_path):
    # Mocking docx.Document to avoid needing a real file
    with patch('extract_docx.docx.Document', create=True) as mock_document:
        # Create a mock document with paragraphs
        mock_doc_instance = MagicMock()

        # Create mock paragraphs with 'text' attribute
        mock_p1 = MagicMock()
        mock_p1.text = "Paragraph 1"
        mock_p2 = MagicMock()
        mock_p2.text = "Paragraph 2"

        mock_doc_instance.paragraphs = [mock_p1, mock_p2]
        mock_document.return_value = mock_doc_instance

        result = extract_docx.extract_text_from_docx("dummy.docx")

        assert result == "Paragraph 1\nParagraph 2"
        mock_document.assert_called_once_with("dummy.docx")

@patch('sys.argv', ['extract_docx.py', 'test.docx'])
@patch('sys.stdout')
@patch('extract_docx.extract_text_from_docx')
def test_main_happy_path(mock_extract, mock_stdout):
    mock_extract.return_value = "Mocked content"

    # Should not raise any exception and not exit
    extract_docx.main()

    mock_extract.assert_called_once_with('test.docx')
    # Can't easily assert print without reading stdout, but patch is fine

@patch('sys.argv', ['extract_docx.py'])
@patch('sys.exit')
@patch('sys.stdout')
def test_main_missing_args(mock_stdout, mock_exit):
    extract_docx.main()
    mock_exit.assert_called_once_with(1)

@patch('sys.argv', ['extract_docx.py', 'test.docx'])
@patch('sys.exit')
@patch('sys.stdout')
@patch('extract_docx.extract_text_from_docx')
def test_main_extraction_error(mock_extract, mock_stdout, mock_exit):
    mock_extract.side_effect = Exception("mock error")

    extract_docx.main()

    mock_extract.assert_called_once_with('test.docx')
    mock_exit.assert_called_once_with(1)
