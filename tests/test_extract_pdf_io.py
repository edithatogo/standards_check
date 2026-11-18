import os
import sys
import pytest
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_pdf_content import extract_text_from_pdf

def test_extract_text_from_pdf_exception(capsys):
    """
    Test that when an exception occurs during PDF text extraction
    (e.g., pdfplumber fails to open the file), the function gracefully
    catches the exception, prints an error message, and returns None.
    """
    with patch('pdfplumber.open', side_effect=Exception('Simulated PDF extraction error')):
        result = extract_text_from_pdf('dummy.pdf')
        assert result is None

        # Verify that the error message is printed to stdout
        captured = capsys.readouterr()
        assert "Error extracting text from dummy.pdf: Simulated PDF extraction error" in captured.out

def test_extract_text_from_pdf_success(tmp_path):
    """
    Test the happy path where a PDF is successfully opened and text extracted.
    """
    pdf_path = str(tmp_path / 'dummy.pdf')
    output_path = str(tmp_path / 'dummy_extracted.txt')

    # We create a mock pdf object that returns pages when iterated over
    class MockPage:
        def extract_text(self):
            return "Test content page"

    class MockPDF:
        pages = [MockPage(), MockPage()]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch('pdfplumber.open', return_value=MockPDF()):
        result = extract_text_from_pdf(pdf_path, output_path)

        # Verify the returned content
        assert "Test content page\n\nTest content page\n\n" == result

        # Verify the content was written to the output file
        assert os.path.exists(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Test content page\n\nTest content page\n\n" == content

def test_extract_text_from_pdf_success_no_output_path(tmp_path):
    """
    Test the happy path where no output path is given, so it defaults to generating one.
    """
    pdf_path = str(tmp_path / 'my_doc.pdf')

    # We create a mock pdf object that returns pages when iterated over
    class MockPage:
        def extract_text(self):
            return "Content without output path"

    class MockPDF:
        pages = [MockPage()]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    # Change to the tmp_path directory so the default output file is created there
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch('pdfplumber.open', return_value=MockPDF()):
            result = extract_text_from_pdf(pdf_path)

            # Verify the returned content
            assert "Content without output path\n\n" == result

            # Default output name should be 'my_doc_extracted.txt' in the current working dir
            expected_output = "my_doc_extracted.txt"
            assert os.path.exists(expected_output)
            with open(expected_output, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Content without output path\n\n" == content
    finally:
        os.chdir(original_cwd)

def test_extract_multiple_pdfs(tmp_path):
    """
    Test extraction of multiple PDFs from a directory.
    """
    source_dir = tmp_path / "pdfs"
    output_dir = tmp_path / "output"

    source_dir.mkdir()

    # Create some dummy pdf files
    (source_dir / "doc1.pdf").write_text("dummy")
    (source_dir / "doc2.pdf").write_text("dummy")

    # We mock extract_text_from_pdf since we already tested it directly
    with patch('scripts.extract_pdf_content.extract_text_from_pdf') as mock_extract:
        from scripts.extract_pdf_content import extract_multiple_pdfs
        extract_multiple_pdfs(str(source_dir), str(output_dir))

        # Should be called twice (for doc1.pdf and doc2.pdf)
        assert mock_extract.call_count == 2

        # Verify call arguments
        calls = mock_extract.call_args_list
        # Output file paths
        out1 = str(output_dir / "doc1_extracted.txt")
        out2 = str(output_dir / "doc2_extracted.txt")

        # Get all positional arguments from all calls
        called_args = [call[0] for call in calls]

        # Extract both source and dest paths that were called
        called_source_dest = {(args[0], args[1]) for args in called_args}

        expected_source_dest = {
            (str(source_dir / "doc1.pdf"), out1),
            (str(source_dir / "doc2.pdf"), out2),
        }

        assert called_source_dest == expected_source_dest

def test_extract_multiple_pdfs_no_pdfs(tmp_path, capsys):
    """
    Test multiple extraction when directory has no PDFs.
    """
    source_dir = tmp_path / "empty_dir"
    output_dir = tmp_path / "output"

    source_dir.mkdir()

    from scripts.extract_pdf_content import extract_multiple_pdfs
    extract_multiple_pdfs(str(source_dir), str(output_dir))

    captured = capsys.readouterr()
    assert f"No PDF files found in {str(source_dir)}" in captured.out

def test_main_missing_args():
    from scripts.extract_pdf_content import main
    with patch('sys.argv', ['extract_pdf_content.py']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

def test_main_directory_mode(tmp_path):
    from scripts.extract_pdf_content import main
    with patch('sys.argv', ['extract_pdf_content.py', str(tmp_path), '-d', '-o', str(tmp_path / 'out')]):
        with patch('scripts.extract_pdf_content.extract_multiple_pdfs') as mock_multi:
            main()
            mock_multi.assert_called_once_with(str(tmp_path), str(tmp_path / 'out'))

def test_main_single_file_mode(tmp_path):
    from scripts.extract_pdf_content import main
    with patch('sys.argv', ['extract_pdf_content.py', str(tmp_path / 'dummy.pdf'), '-o', str(tmp_path / 'out.txt')]):
        with patch('scripts.extract_pdf_content.extract_text_from_pdf') as mock_single:
            main()
            mock_single.assert_called_once_with(str(tmp_path / 'dummy.pdf'), str(tmp_path / 'out.txt'))
