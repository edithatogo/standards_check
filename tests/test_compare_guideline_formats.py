"""Behavioural regressions for family-scoped format evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from scripts.compare_ecoevo_formats import EXPECTED_IDS, collect_rows, compare_formats
from scripts.compare_guideline_formats import (
    Cohort, benchmark, header_roles, profiles, summarize_source,
)
from scripts.structured_source import ITEM_ID, cell_fields


def test_family_header_and_identifier_dialects():
    def table(rows):
        return {"rows": [{"cells": [
            {"column": j, "anchor": f"r{i}/c{j}", **cell_fields(text)}
            for j, text in enumerate(row, 1)]} for i, row in enumerate(rows, 1)]}
    for identifier in ("1", "12b", "S21"):
        rows, issues = collect_rows(
            table([["Score", "Item number", "Recommendation"],
                   ["2", identifier, "Report the result."]]),
            identifier_pattern=ITEM_ID, header_roles=header_roles(),
        )
        assert [r["item_id"] for r in rows] == [identifier]
        assert rows[0]["requirement_anchor"] == "r2/c3"
        assert not issues
    assert len(EXPECTED_IDS) == 89


def test_pairwise_denominator_and_duplicates():
    def row(identifier, digest):
        return {"item_id": identifier, "requirement_sha256": digest}
    a = [row("1", "a"), row("2a", "b"), row("2a", "b"), row("9", "z")]
    b = [row("1", "c"), row("2a", "b"), row("9", "z")]
    result = compare_formats(a, b, expected_ids=["1", "2a", "3"])
    assert result == {"compared": 1, "exact_equal": 0, "different_ids": ["1"],
                      "not_comparable_expected_ids": ["2a", "3"]}


def test_independent_family_references_not_legacy_views():
    by_id = {p.edition: p for p in profiles(Path("."))}
    for edition, count in {"prisma-ecoevo-2021": 89, "consort-2025": 42,
                           "spirit-2025": 53, "stard-2015": 34,
                           "srqr-2014": 21, "cheers-2022": 28,
                           "tripod-ai-2024": 52, "prisma-p-2015": 26}.items():
        assert len(by_id[edition].expected_ids) == count
    assert by_id["strobe-2007"].expected_ids == ()
    assert by_id["tripod-ai-2024"].paths == ()
    assert not any("tripod-2015" in p for p in by_id["tripod-ai-2024"].paths)
    assert by_id["srqr-2014"].expected_ids[-1] == "S21"


def test_real_csv_and_html_with_negative_cases(tmp_path):
    csv = tmp_path / "a.csv"
    csv.write_text("Item number,Recommendation,Score\n1,Report the result.,9\n2a,Report limitations.,8\n", encoding="utf-8")
    html = tmp_path / "b.html"
    html.write_text("<table><tr><th>Item number</th><th>Recommendation</th></tr>"
                    "<tr><td>1</td><td>Do not report the result.</td></tr>"
                    "<tr><td>2a</td><td>Report limitations.</td></tr>"
                    "<tr><td>2a</td><td>Report limitations.</td></tr></table>", encoding="utf-8")
    profile = Cohort("synthetic-2026", "synthetic", ("1", "2a", "3"),
                     ("a.csv", "b.html", "missing.pdf"), "synthetic reference")
    report = benchmark(tmp_path, [profile])
    edition = report["editions"][0]
    a, b, missing = edition["sources"]
    assert a["source_sha256"] == hashlib.sha256(csv.read_bytes()).hexdigest()
    assert a["missing_ids"] == ["3"]
    assert b["duplicate_ids"] == ["2a"]
    assert missing["status"] == "held_unavailable_or_unsupported"
    pair = edition["pairwise"][0]
    assert pair["different_ids"] == ["1"]
    assert pair["not_comparable_expected_ids"] == ["2a", "3"]
    assert pair["cross_format"]
    assert report["canonical_packs_promoted"] == 0
    assert "Report the result." not in json.dumps(report)
    assert report == benchmark(tmp_path, [profile])


def test_unknown_denominator_and_missing_anchor_are_not_success():
    report = summarize_source([{"item_id": "1", "requirement_sha256": "a" * 64,
                                "identifier_anchor": None, "requirement_anchor": "r1"}],
                              (), [])
    assert report["expected_ids_recovered"] is None
    assert report["missing_ids"] is None
    assert report["exact_expected_order"] is None
    assert report["rows"][0]["requirement_sha256"] is None
    assert "missing_row_anchor" in report["issues"]


def test_reject_duplicate_reference_and_path_escape(tmp_path):
    with pytest.raises(ValueError):
        benchmark(tmp_path, [Cohort("bad", "test", ("1", "1"), (), "reference")])
    with pytest.raises(ValueError):
        benchmark(tmp_path, [Cohort("bad", "test", ("1",), ("../x.csv",), "reference")])


def test_absent_family_is_reported_without_pairwise_success(tmp_path):
    result = benchmark(tmp_path, [Cohort("unavailable", "test", ("1",), (), "reference")])
    edition = result["editions"][0]
    assert edition["status"] == "held_no_candidate_sources"
    assert not edition["pairwise"]
