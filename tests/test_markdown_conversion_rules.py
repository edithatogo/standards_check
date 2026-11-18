import pytest
import sys
import os

# Add the parent directory to the sys.path so we can import from extract_and_convert
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extract_and_convert import convert_to_markdown_format

def test_convert_title_format():
    """Test that the title is correctly formatted from the filename."""
    text = "Some text"
    filename = "my-test-file.docx"
    result = convert_to_markdown_format(text, filename)

    # Title logic: filename.replace('.docx', '').replace('-', ' ').title()
    # "my-test-file" -> "My Test File"
    assert "# My Test File Checklist" in result

def test_convert_instructions_insertion():
    """Test that the hardcoded instructions are inserted correctly."""
    text = "Some text"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)

    assert "## Instructions" in result
    assert "- Use task list items for checklist boxes; these become interactive checkboxes in PDF." in result
    assert "- Use a span with class `.textfield` for free‑text fields." in result
    assert "- Report all applicable items from the checklist." in result

def test_section_header_detection():
    """Test that section headers are detected and formatted correctly."""
    text = "UPPERCASE SECTION\nShort Title Case\nThis Is A Much Longer Title Case That Should Be Ignored\nregular text that is long"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)

    # UPPERCASE SECTION should be a header
    assert "## UPPERCASE SECTION" in result
    # Short Title Case should be a header (3 words <= 5)
    assert "## Short Title Case" in result
    # The longer title case should NOT be a header (11 words > 5)
    assert "## This Is A Much Longer Title Case That Should Be Ignored" not in result
    assert "This Is A Much Longer Title Case That Should Be Ignored" in result
    # Regular text should remain regular text
    assert "regular text that is long" in result

def test_checklist_item_extraction():
    """Test that checklist items are correctly detected and formatted."""
    text = "1. First item\na) Second item\n* Third item\n- Fourth item\n• Fifth item\nText that is not a list item and is quite long"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)

    # All items should have the list marker stripped and "- [ ] " prepended
    assert "- [ ] First item" in result
    assert "- [ ] Second item" in result
    assert "- [ ] Third item" in result
    assert "- [ ] Fourth item" in result
    assert "- [ ] Fifth item" in result
    assert "Text that is not a list item and is quite long" in result

def test_empty_line_handling():
    """Test that empty lines are skipped and don't create empty markdown output lines."""
    # We use longer strings so they aren't parsed as Title Case section headers
    text = "This is the first regular line\n\n\nThis is the second regular line"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)

    lines = result.split('\n')
    # Check occurrences of our specific lines
    assert "This is the first regular line" in lines
    assert "This is the second regular line" in lines

    # There should only be two empty lines in the output: one after the title, one after instructions.
    # The input empty lines should be ignored.
    empty_lines_count = sum(1 for line in lines if not line.strip())
    assert empty_lines_count == 2
