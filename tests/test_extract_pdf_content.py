import os
import sys
from pathlib import Path
import pytest

# Add the scripts directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from extract_pdf_content import extract_text_from_pdf, extract_multiple_pdfs

class MockPage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text

class MockPDF:
    def __init__(self, pages):
        self.pages = [MockPage(p) for p in pages]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def mock_pdfplumber_open(mocker):
    def _mock_open(pages_text):
        mock_pdf = MockPDF(pages_text)
        return mocker.patch('pdfplumber.open', return_value=mock_pdf)
    return _mock_open

def test_extract_text_from_pdf_success(tmp_path, mock_pdfplumber_open):
    # Setup mock PDF with two pages
    mock_pdfplumber_open(["Page 1 content", "Page 2 content"])

    pdf_path = "dummy.pdf"
    output_path = tmp_path / "output.txt"

    # Call function
    extracted_text = extract_text_from_pdf(pdf_path, str(output_path))

    # Assertions
    expected_text = "Page 1 content\n\nPage 2 content\n\n"
    assert extracted_text == expected_text

    # Verify file was written
    assert output_path.exists()
    assert output_path.read_text(encoding='utf-8') == expected_text

def test_extract_text_from_pdf_default_output(tmp_path, mock_pdfplumber_open, mocker):
    # Setup mock PDF
    mock_pdfplumber_open(["Single page content"])

    # Create a dummy pdf file so it has a path, use tmp_path as current dir essentially
    # We will patch Path.cwd to tmp_path or just use relative path in tmp_path
    pdf_path = tmp_path / "my_document.pdf"

    # We want the output to be created in the current working directory as per the script
    # Wait, the script does `output_path = f"{pdf_name}_extracted.txt"` where `pdf_name = Path(pdf_path).stem`
    # This writes to the current working directory where the script is executed.

    # Let's mock open to intercept where it's written
    m_open = mocker.patch("builtins.open", mocker.mock_open())

    # Call function without specifying output_path
    extracted_text = extract_text_from_pdf(str(pdf_path))

    expected_text = "Single page content\n\n"
    assert extracted_text == expected_text

    # Verify open was called with the correct default filename
    m_open.assert_called_once_with("my_document_extracted.txt", 'w', encoding='utf-8')
    m_open().write.assert_called_once_with(expected_text)

def test_extract_text_from_pdf_exception(mocker):
    # Setup mock to raise an exception when opening
    mocker.patch('pdfplumber.open', side_effect=Exception("Failed to open PDF"))

    # Call function
    extracted_text = extract_text_from_pdf("error.pdf", "out.txt")

    # Assertions
    assert extracted_text is None

def test_extract_multiple_pdfs(tmp_path, mocker):
    # Create dummy source and output directories
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    source_dir.mkdir()

    # Create some dummy pdf files
    (source_dir / "doc1.pdf").touch()
    (source_dir / "doc2.pdf").touch()

    # Mock extract_text_from_pdf
    m_extract = mocker.patch('extract_pdf_content.extract_text_from_pdf')

    # Call function
    extract_multiple_pdfs(str(source_dir), str(output_dir))

    # Assertions
    assert output_dir.exists()
    assert m_extract.call_count == 2

    # Check arguments
    calls = m_extract.call_args_list
    args_called = [ (c[0][0], c[0][1]) for c in calls ]

    # Paths will depend on glob order, so we check sets
    expected_args = {
        (str(source_dir / "doc1.pdf"), str(output_dir / "doc1_extracted.txt")),
        (str(source_dir / "doc2.pdf"), str(output_dir / "doc2_extracted.txt"))
    }
    assert set(args_called) == expected_args

def test_extract_multiple_pdfs_no_files(tmp_path, mocker):
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    source_dir.mkdir()

    m_extract = mocker.patch('extract_pdf_content.extract_text_from_pdf')

    # Call function on empty directory
    extract_multiple_pdfs(str(source_dir), str(output_dir))

    # Should not be called
    m_extract.assert_not_called()
