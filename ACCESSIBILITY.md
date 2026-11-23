# Accessibility

StandardFlow aims to make reporting checklists, diagrams, documentation and generated
artefacts usable by people with different access needs. **This is a statement of intent,
not a WCAG conformance certificate.** No independent end-to-end accessibility audit has
been completed for the repository, its published website or all generated formats.

## What this covers

- **Website and Markdown:** The HTML site and repository documentation aim for semantic
  headings, meaningful links, keyboard operation and screen-reader navigation. These
  behaviours have not been independently verified across browsers and assistive technologies.
- **Diagrams:** The maintained Rust artefact engine generates structured SVG alongside
  text and scene-JSON views for selected PRISMA flows. Text equivalents are intended to
  reduce dependence on colour and spatial layout, but full keyboard, screen-reader,
  contrast and zoom acceptance remains open.
- **Documents:** PDF, DOCX, Typst and LaTeX are derived from source material. PDF tagging,
  accessible reading order, form control labelling and assistive-technology interoperability
  are not established for every generated file. Where possible, try the corresponding
  Markdown, HTML or text version if a PDF or diagram is inaccessible.
- **CLI and legacy application:** The Rust CLI offers text and machine-readable outputs.
  The retained Python/Graphviz legacy surface may behave differently and is not covered
  by the canonical engine's limited regression evidence.

The [Conductor accessibility and quality track](conductor/tracks/05-maximal-assurance/spec.md)
separates automated validation from independent accessibility qualification. WCAG 2.2
Level AA is an aspirational reference for relevant web interfaces, **not a claim of current
compliance**.

## Report an accessibility barrier

[Open an accessibility issue](https://github.com/edithatogo/standards_check/issues/new?template=accessibility_issue.md)
or use the [issue tracker](https://github.com/edithatogo/standards_check/issues).
Include the URL or file/command and commit or version, what you were trying to do,
what happened, what would make it usable and (if comfortable) browser, operating
system or assistive technology. A small synthetic example is helpful.

Avoid posting sensitive health information, private records, credentials, personal
details or copyrighted standards text. If the concern contains a vulnerability,
use the [security policy](SECURITY.md) instead of a public issue.
For other help, see [Support](SUPPORT.md).

Accessibility issues will be triaged by severity, user impact and available
maintenance capacity. There is no guaranteed response time or release schedule.
Contributors can propose accessible alternatives with reproducible tests and,
where appropriate, text equivalents without removing existing validation.

## Maintaining this statement

Update this page when supported outputs, known barriers or accessibility evidence
change. Do not replace an independent manual assessment with an automated score.
