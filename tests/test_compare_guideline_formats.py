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


def test_pinned_article_snapshot_is_compared_without_raw_text():
    from dataclasses import replace

    cohort = next(p for p in profiles(Path(".")) if p.edition == "cheers-2022")
    result = benchmark(Path("."), [replace(cohort, paths=())])
    source = result["editions"][0]["sources"][0]
    assert source["format"] == "jats_snapshot"
    assert source["expected_ids_recovered"] == 28
    assert source["identity"] == "retained_table_snapshot_matches_pinned_rows"
    assert len(source["table_rows_sha256"]) == 64
    assert all(len(row["requirement_sha256"]) == 64 for row in source["rows"])
    assert all("text" not in row for row in source["rows"])


def test_ambiguous_header_is_held(tmp_path):
    (tmp_path / "ambiguous.csv").write_text(
        "Item number,Item ID,Recommendation\n1,2,Report results.\n", encoding="utf-8")
    cohort = Cohort("synthetic", "test", ("1",), ("ambiguous.csv",), "reference")
    source = benchmark(tmp_path, [cohort])["editions"][0]["sources"][0]
    assert source["expected_ids_recovered"] == 0
    assert "incomplete_or_ambiguous_header" in source["issues"]
    assert source["status"] == "held_structural_discrepancy"


def test_same_bytes_and_no_comparable_pairs_stay_labelled(tmp_path):
    data = "Item number,Recommendation\n1,Report results.\n"
    for name in ("a.csv", "b.csv"):
        (tmp_path / name).write_text(data, encoding="utf-8")
    cohort = Cohort("synthetic", "test", ("1", "2"), ("a.csv", "b.csv", "absent.csv"), "reference")
    edition = benchmark(tmp_path, [cohort])["editions"][0]
    first, second, _ = edition["pairwise"]
    assert first["identical_source_bytes"] is True
    assert first["cross_format"] is False
    assert first["independent_source_identity_verified"] is False
    assert second["identical_source_bytes"] is None
    assert second["status"] == "held_no_comparable_rows"
    assert edition["sources"][0]["status"] == "held_structural_discrepancy"
    assert "missing_expected_ids" in edition["sources"][0]["issues"]


def test_cli_receipt_is_deterministic_and_references_are_hashed(tmp_path, monkeypatch):
    import sys
    from scripts import compare_guideline_formats as driver

    for relative in (driver.ARTICLE_SPECS, driver.ARTICLE_ROWS, driver.PRIORITY, driver.HELD):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"[]")
    monkeypatch.setattr(driver, "profiles", lambda root: [Cohort("synthetic", "test", (), (), "reference")])
    output = tmp_path / "out" / "report.json"
    monkeypatch.setattr(sys, "argv", ["compare_guideline_formats", "--root", str(tmp_path), "--output", str(output)])
    driver.main()
    first = output.read_bytes()
    assert len(json.loads(first)["reference_files_sha256"]) == 4
    driver.main()
    assert output.read_bytes() == first


def test_symlink_and_duplicate_cohort_rejected(tmp_path):
    path = tmp_path / "real.csv"
    path.write_text("Item number,Recommendation\n1,Report results.\n", encoding="utf-8")
    (tmp_path / "link.csv").symlink_to(path)
    with pytest.raises(ValueError, match="symlink"):
        benchmark(tmp_path, [Cohort("synthetic", "test", ("1",), ("link.csv",), "reference")])
    profile = Cohort("synthetic", "test", ("1",), (), "reference")
    with pytest.raises(ValueError, match="duplicate"):
        benchmark(tmp_path, [profile, profile])


def test_ecoevo_keeps_subitem_dialect_in_family_driver(tmp_path):
    (tmp_path / "ecoevo.csv").write_text(
        "Item number,Sub-item number,Sub-item,Score\n1,1.1,Report results.,2\n", encoding="utf-8")
    cohort = Cohort("prisma-ecoevo-2021", "prisma", ("1.1",), ("ecoevo.csv",), "synthetic")
    source = benchmark(tmp_path, [cohort])["editions"][0]["sources"][0]
    assert source["expected_ids_recovered"] == 1
    assert source["rows"][0]["requirement_sha256"] is not None
    assert "incomplete_or_ambiguous_header" not in source["issues"]


def test_ecoevo_pdf_reuses_independent_grid_evidence(tmp_path):
    from tests.test_ecoevo_grid import tiny_grid_pdf
    (tmp_path / "ecoevo.pdf").write_bytes(tiny_grid_pdf())
    cohort = Cohort("prisma-ecoevo-2021", "prisma", ("1.1", "1.2", "1.3"),
                    ("ecoevo.pdf",), "synthetic")
    source = benchmark(tmp_path, [cohort])["editions"][0]["sources"][0]
    assert source["expected_ids_recovered"] == 3
    assert source["independent_pdf"]["expected_ids_recovered"] == 3
    assert source["independent_pdf"]["layout_comparison"]["exact_equal"] == 3
