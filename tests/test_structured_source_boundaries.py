"""Generated CSV invariants and hostile document structures remain candidate evidence."""

import csv
import io

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from hypothesis import given, settings, strategies as st
import pytest

from scripts import structured_source as source


@settings(max_examples=64, derandomize=True)
@given(
    rows=st.lists(
        st.lists(
            st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=24),
            min_size=2,
            max_size=2,
        ),
        min_size=1,
        max_size=15,
    )
)
def test_csv_writer_roundtrip_preserves_row_cell_denominators_and_hashes(rows):
    output = io.StringIO(newline="")
    csv.writer(output).writerows(rows)
    _, report = source.extract_structure(output.getvalue().encode("utf-8"), ".csv")
    assert report["status"] == "structure_observed_not_qualified"
    assert len(report["rows"]) == len(rows)
    for original, observed in zip(rows, report["rows"], strict=True):
        assert len(observed["cells"]) == len(original)
        assert [cell["text_sha256"] for cell in observed["cells"]] == [
            source.fingerprint(value) for value in original
        ]
    anchors = [cell["anchor"] for row in report["rows"] for cell in row["cells"]]
    assert len(anchors) == len(set(anchors))


def docx_bytes(document):
    stream = io.BytesIO()
    document.save(stream)
    return stream.getvalue()


def test_docx_unresolved_numbering_and_nonbody_content_stay_held():
    document = Document()
    paragraph = document.add_paragraph("Synthetic requirement")
    numbering = OxmlElement("w:numPr")
    number = OxmlElement("w:numId")
    number.set(qn("w:val"), "99")
    numbering.append(number)
    paragraph._p.get_or_add_pPr().append(numbering)
    document.sections[0].header.paragraphs[0].text = "Unextracted header requirement"
    document._element.body.append(OxmlElement("w:sdt"))
    text, report = source.extract_structure(docx_bytes(document), ".docx")
    assert "Unextracted header requirement" not in text
    assert report["status"] == "held_structural_discrepancy"
    assert {
        "rendered_numbering_not_resolved",
        "non_body_parts_not_extracted",
        "complex_docx_content_not_fully_extracted",
        "unsupported_docx_block",
    } <= set(report["issues"])


def test_docx_orphaned_vertical_merge_cannot_claim_a_complete_grid():
    document = Document()
    table = document.add_table(rows=1, cols=1)
    cell = table.cell(0, 0)
    cell.text = "Orphan continuation"
    merge = OxmlElement("w:vMerge")
    cell._tc.get_or_add_tcPr().append(merge)
    _, report = source.extract_structure(docx_bytes(document), ".docx")
    assert {"unbound_vertical_merge", "nonempty_vertical_continuation"} <= set(report["issues"])


@pytest.mark.parametrize("limit", ["MAX_DEPTH", "MAX_CELLS"])
def test_docx_nesting_and_structure_budgets_fail_closed(monkeypatch, limit):
    document = Document()
    document.add_table(rows=1, cols=1).cell(0, 0).text = "Nested text"
    monkeypatch.setattr(source, limit, 0)
    with pytest.raises(ValueError, match="exceeds limit"):
        source.extract_structure(docx_bytes(document), ".docx")


def test_csv_and_html_budgets_are_enforced_before_complete_receipts(monkeypatch):
    monkeypatch.setattr(source, "MAX_CELLS", 1)
    with pytest.raises(ValueError, match="CSV structure exceeds"):
        source.extract_structure(b"1,requirement", ".csv")
    with pytest.raises(ValueError, match="HTML structure exceeds"):
        source.extract_structure(b"<table><tr><td>Requirement</td></tr></table>", ".html")


@pytest.mark.parametrize(
    "raw, expected",
    [
        (
            b"<table><caption>Text<img src='untrusted'></caption></table>",
            {"empty_html_table", "unsupported_caption_content"},
        ),
        (
            b"<table><unexpected>Unknown</unexpected><tr><td>1<!-- note -->a</td></tr></table>",
            {"unsupported_table_child"},
        ),
    ],
)
def test_unsupported_static_content_is_explicitly_held(raw, expected):
    _, report = source.extract_structure(raw, ".html")
    assert expected <= set(report["issues"])
    assert report["status"] == "held_structural_discrepancy"


def test_html_span_overlap_cannot_duplicate_source_positions():
    raw = b"<table><tr><td>one</td><td rowspan='2'>two</td></tr><tr><td colspan='2'>overlap</td></tr></table>"
    with pytest.raises(ValueError, match="overlapping"):
        source.extract_structure(raw, ".html")
