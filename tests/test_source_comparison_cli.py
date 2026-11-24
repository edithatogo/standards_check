"""CLI evidence binds actual local source bytes and retains negative results."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import compare_prisma_source_pdf as prisma
from scripts import compare_ecoevo_formats as ecoevo

ROOT = Path(__file__).resolve().parents[1]


def test_prisma_cli_compares_the_pinned_local_pdf_without_network(tmp_path):
    output = tmp_path / "comparison.json"
    pdf = ROOT / "source/official/prisma-2020-checklist.pdf"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.compare_prisma_source_pdf",
            "--pdf",
            str(pdf),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text())
    assert receipt["item_count"] == 42
    assert receipt["pdf_sha256"] == hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert receipt["status"] == "machine_compared_source_text"
    assert (
        "Human methodological and translation evaluation are not covered" in receipt["limitations"]
    )


def test_bad_pdf_cli_does_not_replace_a_previous_receipt(tmp_path):
    output, pdf = tmp_path / "receipt.json", tmp_path / "changed.pdf"
    output.write_text("previous receipt")
    pdf.write_bytes(b"not the pinned original")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.compare_prisma_source_pdf",
            "--pdf",
            str(pdf),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "pinned original" in result.stderr
    assert output.read_text() == "previous receipt"


def test_unexpected_pdf_page_count_and_page_item_binding_fail():
    with pytest.raises(ValueError, match="Unexpected PDF page"):
        prisma.checklist_column("row", 3)
    with pytest.raises(ValueError, match="exactly two pages"):
        prisma.numbered_rows(["only one page"])
    with pytest.raises(ValueError, match="Unexpected item 1 on PDF page 2"):
        prisma.numbered_rows(["", "1".rjust(prisma.GUTTERS[2]) + "wrong page"])


def test_ecoevo_cli_retains_absent_sources_as_holds_and_hashes_input_bytes(tmp_path):
    report = tmp_path / "triage.json"
    report.write_text(
        json.dumps(
            {
                "schema_version": 3,
                "summary": {"verified_by_this_process": 0},
                "legacy_items": [{"legacy_id": "prisma-ecoevo", "source_probes": []}],
            }
        )
    )
    output = tmp_path / "evidence/comparison.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.compare_ecoevo_formats",
            "--report",
            str(report),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text())
    assert receipt["triage_report_sha256"] == hashlib.sha256(report.read_bytes()).hexdigest()
    assert receipt["canonical_packs_promoted"] == 0
    assert len(receipt["sources"]) == len(ecoevo.COHORT)
    assert all(row["expected_ids_recovered"] == 0 for row in receipt["sources"])
    assert all("structure_unavailable" in row["issues"] for row in receipt["sources"])
