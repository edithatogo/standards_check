import os
import sys
from pathlib import Path

# Add the project root to the path so we can import from scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.extract_pdf_content import extract_multiple_pdfs

def test_extract_multiple_pdfs_empty_directory(tmp_path, mocker):
    """Test behavior when the source directory contains no PDFs."""
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    source_dir.mkdir()

    # Create a non-PDF file to ensure it's ignored
    (source_dir / "not_a_pdf.txt").write_text("Hello")

    mock_extract = mocker.patch('scripts.extract_pdf_content.extract_text_from_pdf')

    extract_multiple_pdfs(str(source_dir), str(output_dir))

    assert output_dir.exists(), "Output directory should be created even if empty"
    mock_extract.assert_not_called(), "Should not call extraction if no PDFs exist"


def test_extract_multiple_pdfs_with_pdfs(tmp_path, mocker):
    """Test extraction iteration with multiple PDF files."""
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    source_dir.mkdir()

    # Create dummy PDF files
    pdf1 = source_dir / "doc1.pdf"
    pdf2 = source_dir / "doc2.pdf"
    pdf1.touch()
    pdf2.touch()

    # Create a non-PDF file to ensure it's ignored
    (source_dir / "not_a_pdf.txt").write_text("Hello")

    mock_extract = mocker.patch('scripts.extract_pdf_content.extract_text_from_pdf')

    extract_multiple_pdfs(str(source_dir), str(output_dir))

    assert output_dir.exists(), "Output directory should be created"
    assert mock_extract.call_count == 2, "Should call extraction exactly twice"

    # Verify the calls were made with correct arguments
    expected_calls = [
        mocker.call(str(pdf1), str(output_dir / "doc1_extracted.txt")),
        mocker.call(str(pdf2), str(output_dir / "doc2_extracted.txt"))
    ]
    mock_extract.assert_has_calls(expected_calls, any_order=True)
