import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add scripts directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_pdf_content import extract_text_from_pdf, extract_multiple_pdfs, main

@patch('scripts.extract_pdf_content.pdfplumber.open')
@patch('builtins.open', new_callable=mock_open)
def test_extract_text_from_pdf_success_explicit_output(mock_file, mock_pdf_open):
    # Setup mock PDF
    mock_pdf = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 text"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 text"
    mock_pdf.pages = [mock_page1, mock_page2]
    mock_pdf_open.return_value.__enter__.return_value = mock_pdf

    result = extract_text_from_pdf("dummy.pdf", "output.txt")

    # Assertions
    mock_pdf_open.assert_called_once_with("dummy.pdf")
    mock_file.assert_called_once_with("output.txt", 'w', encoding='utf-8')
    mock_file().write.assert_called_once_with("Page 1 text\n\nPage 2 text\n\n")
    assert result == "Page 1 text\n\nPage 2 text\n\n"

@patch('scripts.extract_pdf_content.pdfplumber.open')
@patch('builtins.open', new_callable=mock_open)
def test_extract_text_from_pdf_success_implicit_output(mock_file, mock_pdf_open):
    # Setup mock PDF
    mock_pdf = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 text"
    mock_pdf.pages = [mock_page1]
    mock_pdf_open.return_value.__enter__.return_value = mock_pdf

    result = extract_text_from_pdf("dummy.pdf")

    # Assertions
    mock_pdf_open.assert_called_once_with("dummy.pdf")
    mock_file.assert_called_once_with("dummy_extracted.txt", 'w', encoding='utf-8')
    mock_file().write.assert_called_once_with("Page 1 text\n\n")
    assert result == "Page 1 text\n\n"

@patch('scripts.extract_pdf_content.pdfplumber.open')
def test_extract_text_from_pdf_exception(mock_pdf_open):
    # Setup mock to raise exception
    mock_pdf_open.side_effect = Exception("PDF error")

    result = extract_text_from_pdf("dummy.pdf")

    # Assertions
    mock_pdf_open.assert_called_once_with("dummy.pdf")
    assert result is None

@patch('scripts.extract_pdf_content.os.makedirs')
@patch('scripts.extract_pdf_content.Path.glob')
@patch('scripts.extract_pdf_content.extract_text_from_pdf')
def test_extract_multiple_pdfs_found(mock_extract, mock_glob, mock_makedirs):
    # Setup mock glob to return fake paths
    mock_glob.return_value = [Path("source/file1.pdf"), Path("source/file2.pdf")]

    extract_multiple_pdfs("source_dir", "output_dir")

    # Assertions
    mock_makedirs.assert_called_once_with("output_dir", exist_ok=True)
    mock_glob.assert_called_once_with("*.pdf")
    assert mock_extract.call_count == 2

    # Check calls explicitly
    calls = mock_extract.call_args_list
    assert str(calls[0][0][0]) == "source/file1.pdf"
    assert "file1_extracted.txt" in str(calls[0][0][1])
    assert str(calls[1][0][0]) == "source/file2.pdf"
    assert "file2_extracted.txt" in str(calls[1][0][1])

@patch('scripts.extract_pdf_content.os.makedirs')
@patch('scripts.extract_pdf_content.Path.glob')
@patch('scripts.extract_pdf_content.extract_text_from_pdf')
def test_extract_multiple_pdfs_not_found(mock_extract, mock_glob, mock_makedirs):
    # Setup mock glob to return empty
    mock_glob.return_value = []

    extract_multiple_pdfs("source_dir", "output_dir")

    # Assertions
    mock_makedirs.assert_called_once_with("output_dir", exist_ok=True)
    mock_glob.assert_called_once_with("*.pdf")
    mock_extract.assert_not_called()

@patch('scripts.extract_pdf_content.sys.argv', ['extract_pdf_content.py', 'test.pdf'])
@patch('scripts.extract_pdf_content.extract_text_from_pdf')
def test_main_single_file(mock_extract):
    main()
    mock_extract.assert_called_once_with('test.pdf', None)

@patch('scripts.extract_pdf_content.sys.argv', ['extract_pdf_content.py', 'test.pdf', '-o', 'out.txt'])
@patch('scripts.extract_pdf_content.extract_text_from_pdf')
def test_main_single_file_with_output(mock_extract):
    main()
    mock_extract.assert_called_once_with('test.pdf', 'out.txt')

@patch('scripts.extract_pdf_content.sys.argv', ['extract_pdf_content.py', 'source_dir', '-d'])
@patch('scripts.extract_pdf_content.extract_multiple_pdfs')
def test_main_directory(mock_extract_multiple):
    main()
    mock_extract_multiple.assert_called_once_with('source_dir', 'extracted_text')

@patch('scripts.extract_pdf_content.sys.argv', ['extract_pdf_content.py', 'source_dir', '-d', '-o', 'custom_out'])
@patch('scripts.extract_pdf_content.extract_multiple_pdfs')
def test_main_directory_with_output(mock_extract_multiple):
    main()
    mock_extract_multiple.assert_called_once_with('source_dir', 'custom_out')

@patch('scripts.extract_pdf_content.sys.argv', ['extract_pdf_content.py'])
@patch('scripts.extract_pdf_content.sys.exit')
def test_main_no_args(mock_exit):
    main()
    mock_exit.assert_called_once_with(1)
