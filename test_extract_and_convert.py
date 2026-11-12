import pytest
from extract_and_convert import convert_to_markdown_format

def test_convert_to_markdown_format_basic_title():
    text = "Some text"
    filename = "test-document.docx"
    result = convert_to_markdown_format(text, filename)

    # Check title and instructions
    assert "# Test Document Checklist" in result
    assert "## Instructions" in result
    assert "Some text" in result

def test_convert_to_markdown_format_headers():
    text = "INTRODUCTION\nThis is the intro.\nMethodology Section\nMethods here."
    filename = "doc.docx"
    result = convert_to_markdown_format(text, filename)

    assert "## INTRODUCTION\n\nThis is the intro." in result
    assert "## Methodology Section\n\nMethods here." in result

def test_convert_to_markdown_format_checklist_items():
    text = "1. First Item\na) Second item\n* Third item\n- Fourth item"
    filename = "doc.docx"
    result = convert_to_markdown_format(text, filename)

    assert "- [ ] First Item" in result
    assert "- [ ] Second item" in result
    assert "- [ ] Third item" in result
    assert "- [ ] Fourth item" in result

def test_convert_to_markdown_format_empty_and_whitespace():
    text = "\n  \n\t\n"
    filename = "empty.docx"
    result = convert_to_markdown_format(text, filename)

    assert "# Empty Checklist" in result
    assert "## Instructions" in result
    # It shouldn't crash and should just contain the boilerplate

def test_convert_to_markdown_format_filename_without_extension():
    text = "Content"
    filename = "my-file"
    result = convert_to_markdown_format(text, filename)

    assert "# My File Checklist" in result

def test_convert_to_markdown_format_complex_scenario():
    text = """BACKGROUND
1. Outline the problem
2. Provide context
METHODOLOGY
a. Study design
b. Participants
CONCLUSION
Summary of findings"""
    filename = "complex-doc.docx"
    result = convert_to_markdown_format(text, filename)

    assert "## BACKGROUND" in result
    assert "- [ ] Outline the problem" in result
    assert "- [ ] Provide context" in result
    assert "## METHODOLOGY" in result
    assert "- [ ] Study design" in result
    assert "- [ ] Participants" in result
    assert "## CONCLUSION" in result
    assert "Summary of findings" in result
