import sys
import os
import pytest

# Add current directory to path to import extract_and_convert
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extract_and_convert import convert_to_markdown_format

def test_convert_to_markdown_format_title():
    text = "Some text"
    filename = "my-test-document.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert lines[0] == "# My Test Document Checklist"
    assert lines[1] == ""

def test_convert_to_markdown_format_instructions():
    text = "Some text"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "## Instructions" in lines
    assert "- Use task list items for checklist boxes; these become interactive checkboxes in PDF." in lines
    assert "- Use a span with class `.textfield` for free‑text fields." in lines
    assert "- Report all applicable items from the checklist." in lines

def test_convert_to_markdown_format_section_header_upper():
    text = "THIS IS A HEADER"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "## THIS IS A HEADER" in lines

def test_convert_to_markdown_format_section_header_title():
    text = "This Is A Header"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "## This Is A Header" in lines

def test_convert_to_markdown_format_checklist_item_number():
    text = "1. First item\n2) Second item"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "- [ ] First item" in lines
    assert "- [ ] Second item" in lines

def test_convert_to_markdown_format_checklist_item_letter():
    text = "a. First item\nb) Second item"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "- [ ] First item" in lines
    assert "- [ ] Second item" in lines

def test_convert_to_markdown_format_checklist_item_bullet():
    text = "* First item\n- Second item\n• Third item"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "- [ ] First item" in lines
    assert "- [ ] Second item" in lines
    assert "- [ ] Third item" in lines

def test_convert_to_markdown_format_regular_text():
    text = "This is a regular sentence that shouldn't be a header because it is too long."
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')
    assert "This is a regular sentence that shouldn't be a header because it is too long." in lines

def test_convert_to_markdown_format_empty_lines():
    text = "Line 1\n\n\nLine 2"
    filename = "test.docx"
    result = convert_to_markdown_format(text, filename)
    # The empty lines from input are ignored, output empty lines are controlled by the format.
    # We just ensure the valid lines made it.
    assert "Line 1" in result
    assert "Line 2" in result

def test_convert_to_markdown_format_complex():
    text = """INTRODUCTION
This is an introductory text.
1. Check this
2. Check that
METHODS
a. Method 1
b. Method 2"""
    filename = "complex.docx"
    result = convert_to_markdown_format(text, filename)
    lines = result.split('\n')

    assert "# Complex Checklist" in lines
    assert "## INTRODUCTION" in lines
    assert "This is an introductory text." in lines
    assert "- [ ] Check this" in lines
    assert "- [ ] Check that" in lines
    assert "## METHODS" in lines
    assert "- [ ] Method 1" in lines
    assert "- [ ] Method 2" in lines
