# Checklist Transcription Template

Use this template for manually transcribing checklist content from source documents.

## Instructions

1. Copy this template to a new file with the appropriate name
2. Replace placeholder text with actual content
3. Follow the standardized formatting guidelines
4. Add complete provenance information
5. Validate the content before committing

## Template

```markdown
# [Checklist Name]

> Scope: [Brief description of the checklist's scope and purpose]
>
> Reference: [Full citation of the source publication]

## Instructions
- Use task list items for checklist boxes; these become interactive checkboxes in PDF.
- Use a span with class `.textfield` for free‑text fields.
- Report all applicable items from the [checklist name] checklist.

## [Section Name]

- [ ] **[Item Number]. [Item Title]:** [Item description text]

## Provenance
- Source: [URL to the original source]
- Version: [Version/date of the checklist]
- License: [License information]
```

## Common Section Names

- Title and Abstract
- Introduction
- Methods
- Results
- Discussion
- Other Information

## Checklist Item Formatting

### Basic Item
```markdown
- [ ] **1a. Identification:** Description of the item
```

### Item with Sub-items
```markdown
- [ ] **1a. Identification:** Description of the item
  - [ ] Sub-item 1
  - [ ] Sub-item 2
```

### Item with Text Field
```markdown
- [ ] **1a. Identification:** Description of the item
[Additional notes]{.textfield name=item_1a_notes width=12cm}
```

## Provenance Information Requirements

### Required Fields
- Source: Direct URL to the original document
- Version: Publication date or version number
- License: License information (e.g., CC-BY-4.0)

### Optional Fields
- Notes: Additional information about the source or usage

## Example Completed Checklist

```markdown
# CONSORT 2010 Checklist

> Scope: The CONSORT 2010 statement is an evidence-based, minimum set of recommendations for reporting randomised controlled trials.
>
> Reference: Schulz KF, Altman DG, Moher D, for the CONSORT Group. CONSORT 2010 Statement: updated guidelines for reporting parallel group randomised trials. BMJ. 2010;340:c332.

## Instructions
- Use task list items for checklist boxes; these become interactive checkboxes in PDF.
- Use a span with class `.textfield` for free‑text fields.
- Report all applicable items from the CONSORT 2010 checklist.

## Title and Abstract

- [ ] **1a. Identification:** Identification as a randomised trial in the title

## Provenance
- Source: http://www.consort-statement.org/
- Version: 2010
- License: CC-BY-4.0
```