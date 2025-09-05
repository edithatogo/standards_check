# Content Population Workflow

This document describes the workflow for populating checklist content from source documents (PDF, DOCX, etc.) into the standardized Markdown format used in this repository.

## Overview

The content population process involves:
1. Identifying source documents in `source/` directory
2. Extracting content from source documents
3. Formatting content according to the standardized Markdown template
4. Adding provenance information
5. Validating the populated content

## Standardized Markdown Template

All checklist files follow this structure:

```markdown
# Checklist Title

> Scope: Brief description of the checklist's scope and purpose.
>
> Reference: Full citation of the source publication.

## Instructions
- Use task list items for checklist boxes; these become interactive checkboxes in PDF.
- Use a span with class `.textfield` for free‑text fields.
- Report all applicable items from the checklist.

## Section Name

- [ ] **Item Number. Item Title:** Item description text.

## Provenance
- Source: URL to the original source
- Version: Version/date of the checklist
- License: License information
```

## Content Population Steps

### 1. Source Document Identification
- Check `source/archetypes/` and `source/variants/` for source documents
- Look for PDF, DOCX, or CSV files with corresponding YAML sidecar files
- Verify the YAML sidecar contains complete provenance information

### 2. Content Extraction
- For DOCX files: Use `python-docx` library to extract text
- For PDF files: Use `pdfplumber` or `PyPDF2` libraries to extract text
- For CSV files: Direct parsing with Python's `csv` module

### 3. Content Formatting
- Map extracted content to the standardized Markdown template
- Convert checklist items to task list format (`- [ ]`)
- Preserve section hierarchy and numbering
- Add proper formatting for emphasis and references

### 4. Provenance Information
- Copy provenance information from the YAML sidecar file
- Ensure all required fields are present:
  - Source URL
  - Version/date
  - License information
  - Reference citation

### 5. Validation
- Run `scripts/validate_md.sh` to check Markdown formatting
- Verify all checklist items are properly formatted
- Check that provenance information is complete
- Ensure consistency with other checklists of the same family

## Automation Scripts

### DOCX Extraction Script
The `extract_docx.py` script can extract text from DOCX files:

```bash
python extract_docx.py path/to/document.docx
```

### Batch Processing
The `extract_all_docx.py` script processes all DOCX files in the `docx/variants/` directory:

```bash
python extract_all_docx.py
```

## Quality Assurance

### Cross-Reference Checklist
- [ ] All checklist items from source document are included
- [ ] Item numbering matches the source document
- [ ] Section headings are properly formatted
- [ ] Provenance information is complete and accurate
- [ ] Markdown formatting passes validation
- [ ] No placeholder text (TBD, TODO) remains

### Common Issues to Watch For
1. Missing checklist items
2. Incorrect item numbering
3. Incomplete provenance information
4. Improper formatting of task lists
5. Missing or incorrect reference citations

## Best Practices

1. **Consistency**: Maintain consistent formatting across all checklists
2. **Accuracy**: Ensure all content accurately reflects the source document
3. **Completeness**: Include all relevant items from the source document
4. **Attribution**: Provide complete provenance information
5. **Validation**: Always validate content before committing

## Troubleshooting

### python-docx Issues
If experiencing issues with DOCX extraction:
```bash
pip install python-docx
```

### PDF Extraction Issues
For PDF files, install required libraries:
```bash
pip install pdfplumber
```

### Validation Errors
If validation fails:
1. Check the error message for specific issues
2. Review the Markdown formatting against the template
3. Ensure all required sections are present