"""Exact-byte issuer main-ID diagnostics: no external source access in tests."""
import hashlib
import json
from types import SimpleNamespace

import pytest

from scripts.ecoevo_pdf_grid import Word
from scripts.issuer_column_probe import PROFILES, inspect_page, main, observe, summarize_ids


def test_exact_order_and_footnote_identity():
    receipt = summarize_ids(["1", "2*", "3"], ["1", "2*", "3"])
    assert receipt["exact_order"] is True
    assert receipt["observed_ids"] == ["1", "2*", "3"]
    assert receipt["issues"] == []


def test_missing_duplicate_unknown_and_footnote_held():
    receipt = summarize_ids(["1", "1", "2", "bad"], ["1", "2*", "3"])
    assert receipt["exact_order"] is False
    assert set(receipt["issues"]) == {
        "duplicate_ids", "unexpected_ids", "missing_ids", "non_identifier_lines",
        "expected_order_not_recovered",
    }
    assert receipt["missing_ids"] == ["2*", "3"]
    assert receipt["unexpected_ids"] == ["2"]
    assert receipt["non_identifier_count"] == 1
    assert "bad" not in str(receipt)


def test_column_anchor_star_and_nonidentifier():
    words = [
        Word(20, 20, 22, 23, "1"),
        Word(20, 40, 22, 43, "2"),
        Word(22, 40, 23, 43, "*"),
        Word(40, 40, 60, 43, "unrelated text"),
    ]
    result = inspect_page(words, 100, 100, (.18, .1, .25, .9), ["1", "2*"], 1)
    assert result["exact_order"]
    assert result["anchors"][1]["anchor"].startswith("page/1/bbox/")
    assert "unrelated" not in str(result)
    words.extend([Word(20, 60, 22, 63, "7"), Word(22, 60, 24, 63, "8")])
    assert inspect_page(words, 100, 100, (.18, .1, .25, .9), ["1", "2*"], 1)["non_identifier_count"] == 1
    with pytest.raises(ValueError, match="dimensions"):
        inspect_page(words, 0, 100, (.18, .1, .25, .9), ["1"], 1)


def test_observe_and_cli_fail_closed(tmp_path, monkeypatch, capsys):
    import pdfplumber
    import sys

    pdf, bbox, output = (tmp_path / name for name in ("input.pdf", "bbox.xml", "receipt.json"))
    pdf.write_bytes(b"fixture")
    bbox.write_text('<html xmlns="http://www.w3.org/1999/xhtml"><page width="100" height="100"><word xMin="20" yMin="20" xMax="22" yMax="23">1</word></page></html>')
    with pytest.raises(ValueError, match="frozen"):
        observe(pdf, bbox, "arrive")
    monkeypatch.setitem(PROFILES, "arrive", {
        "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "pages": [((.18, .1, .25, .9), ["1"])],
    })

    class FakePDF:
        pages = [SimpleNamespace(width=100, height=100, extract_words=lambda: [
            {"x0": 20, "top": 20, "x1": 22, "bottom": 23, "text": "1"},
        ])]

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    monkeypatch.setattr(pdfplumber, "open", lambda _: FakePDF())
    receipt = observe(pdf, bbox, "arrive")
    assert receipt["all_main_ids_match"] and not receipt["scientific_qualification"]
    assert receipt["canonical_packs_promoted"] == 0
    monkeypatch.setattr(sys, "argv", ["probe", "--family", "arrive", "--pdf", str(pdf),
                                     "--bbox", str(bbox), "--output", str(output)])
    main()
    assert json.loads(output.read_text())["all_main_ids_match"]
    assert "arrive" in capsys.readouterr().out
    bbox.write_text('<html xmlns="http://www.w3.org/1999/xhtml"/>')
    with pytest.raises(ValueError, match="page count"):
        observe(pdf, bbox, "arrive")
    bbox.write_bytes(b"")
    with pytest.raises(ValueError, match="bbox byte limit"):
        observe(pdf, bbox, "arrive")
    pdf.write_bytes(b"")
    with pytest.raises(ValueError, match="PDF byte limit"):
        observe(pdf, bbox, "arrive")
