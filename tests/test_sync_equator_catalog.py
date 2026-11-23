"""Offline, rights-safe tests for EQUATOR directory discovery and metadata parsing."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_equator_catalog.py"
SPEC = importlib.util.spec_from_file_location("equator_catalog", SCRIPT)
assert SPEC and SPEC.loader
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)

SHA = "a" * 40


def test_metadata_is_versioned_deterministic_and_never_copies_checklists(tmp_path):
    page = tmp_path / "reporting-guidelines" / "srqr" / "index.qmd"
    page.parent.mkdir(parents=True)
    page.write_text("""---
title: 'Standards for reporting qualitative research'
acronym: SRQR
rg-doi: 'https://doi.org/10.1097/ACM.0000000000000388'
pmid-id: '[24979285](https://pubmed.ncbi.nlm.nih.gov/24979285/)'
full-bibliographic-reference: 'DO NOT COPY THIS TEXT'
downloads: 'DO NOT DOWNLOAD CHECKLIST CONTENT'
categories:
- Qualitative research
- Qualitative research
clinical-specialty:
- Medical education
report-section:
- Whole report
---
THIS IS GUIDELINE BODY TEXT THAT MUST NEVER BE COPIED
""", encoding="utf-8")
    files = [("reporting-guidelines/srqr/index.qmd", SHA)]
    one = catalog.build_catalog(tmp_path, SHA, files, metadata=True)
    two = catalog.build_catalog(tmp_path, SHA, files, metadata=True)
    assert one == two
    entry = one["guidelines"][0]
    assert entry["doi"] == "10.1097/ACM.0000000000000388"
    assert entry["pmid"] == "24979285"
    assert entry["study_types"] == ["Qualitative research"]
    assert entry["metadata_status"] == "extracted_unverified"
    assert "DO NOT" not in str(one)
    assert "GUIDELINE BODY TEXT" not in str(one)
    assert one["rights_status"] == "not_assessed_for_individual_guidelines"


def test_discovery_does_not_need_guideline_content(tmp_path):
    files = [("reporting-guidelines/srqr/index.qmd", SHA)]
    result = catalog.build_catalog(tmp_path, SHA, files, metadata=False)
    assert result["published_count"] == 1
    assert result["guidelines"][0]["metadata_status"] == "not_extracted"
    assert "title" not in result["guidelines"][0]


def test_missing_or_malformed_page_fails_closed(tmp_path):
    files = [("reporting-guidelines/srqr/index.qmd", SHA)]
    with pytest.raises(ValueError, match="Missing source page"):
        catalog.build_catalog(tmp_path, SHA, files, metadata=True)
    page = tmp_path / files[0][0]
    page.parent.mkdir(parents=True)
    page.write_text("---\ntitle: Missing closing delimiter", encoding="utf-8")
    invalid = catalog.build_catalog(tmp_path, SHA, files, metadata=True)
    assert invalid["guidelines"][0]["metadata_status"] == "needs_review"
    assert "Unterminated" in invalid["guidelines"][0]["metadata_issue"]
    page.write_text("---\ntitle: Valid\ncategories: invalid-scalar\n---\n")
    invalid = catalog.build_catalog(tmp_path, SHA, files, metadata=True)
    assert invalid["guidelines"][0]["metadata_status"] == "needs_review"
    assert "Unexpected categories" in invalid["guidelines"][0]["metadata_issue"]


def test_rejects_unpublished_and_duplicate_ids(tmp_path):
    with pytest.raises(ValueError, match="Not a published"):
        catalog.build_catalog(tmp_path, SHA, [("reporting-guidelines/under-development/index.qmd", SHA)], metadata=False)
    with pytest.raises(ValueError, match="Duplicate"):
        catalog.build_catalog(tmp_path, SHA, [("reporting-guidelines/srqr/index.qmd", SHA)] * 2, metadata=False)


def test_inventory_excludes_development_and_rejects_modified_checkout(tmp_path):
    import subprocess

    def command(*args):
        return subprocess.run(
            ["git", "-C", str(tmp_path), *args],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    command("init", "-q")
    command("config", "user.name", "Unit Test")
    command("config", "user.email", "tests@example.invalid")
    for relative in (
        "reporting-guidelines/srqr/index.qmd",
        "reporting-guidelines/under-development/index.qmd",
        "reporting-guidelines/under-development/proposed/index.qmd",
    ):
        page = tmp_path / relative
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text("---\ntitle: Example\n---\n", encoding="utf-8")
    command("add", "reporting-guidelines")
    command("commit", "-qm", "test")
    head, entries = catalog.inventory(tmp_path)
    assert head == command("rev-parse", "HEAD")
    assert len(entries) == 1
    assert entries[0][0] == "reporting-guidelines/srqr/index.qmd"
    (tmp_path / entries[0][0]).write_text("changed")
    with pytest.raises(ValueError, match="modified"):
        catalog.inventory(tmp_path)


def test_missing_upstream_title_is_preserved_as_review_debt(tmp_path):
    paths = [
        ("reporting-guidelines/srqr/index.qmd", SHA),
        ("reporting-guidelines/strobe-metepi/index.qmd", SHA),
    ]
    for path, title in ((paths[0][0], "SRQR"), (paths[1][0], "")):
        file = tmp_path / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f"---\ntitle: '{title}'\nacronym: TEST\n---\n", encoding="utf-8")
    result = catalog.build_catalog(tmp_path, SHA, paths, metadata=True)
    assert result["published_count"] == 2
    assert result["metadata_issue_count"] == 1
    assert result["guidelines"][0]["metadata_status"] == "extracted_unverified"
    flagged = result["guidelines"][1]
    assert flagged["id"] == "equator:strobe-metepi"
    assert flagged["metadata_status"] == "needs_review"
    assert "Missing guideline title" in flagged["metadata_issue"]
    assert "title" not in flagged


def test_falsey_scalar_lists_are_review_debt(tmp_path):
    path = tmp_path / "reporting-guidelines" / "invalid" / "index.qmd"
    path.parent.mkdir(parents=True)
    path.write_text("---\ntitle: Named\ncategories: 0\n---\n", encoding="utf-8")
    result = catalog.build_catalog(tmp_path, SHA, [("reporting-guidelines/invalid/index.qmd", SHA)], metadata=True)
    assert result["metadata_issue_count"] == 1
    assert "Unexpected categories" in result["guidelines"][0]["metadata_issue"]


def test_nontext_acronyms_and_pmids_are_review_debt(tmp_path):
    path = tmp_path / "reporting-guidelines" / "invalid" / "index.qmd"
    path.parent.mkdir(parents=True)
    entry = ("reporting-guidelines/invalid/index.qmd", SHA)
    path.write_text("---\ntitle: Named\nacronym: 123\n---\n", encoding="utf-8")
    result = catalog.build_catalog(tmp_path, SHA, [entry], metadata=True)
    assert result["guidelines"][0]["metadata_status"] == "needs_review"

    path.write_text("---\ntitle: Named\npmid-id: [12345678]\n---\n", encoding="utf-8")
    result = catalog.build_catalog(tmp_path, SHA, [entry], metadata=True)
    assert result["guidelines"][0]["metadata_status"] == "needs_review"


def test_identifier_fallback_and_ambiguous_values():
    assert catalog._identifiers({"rg-doi": "not a DOI", "pmid-url": "https://pubmed.ncbi.nlm.nih.gov/24979285/"}) == (None, "24979285")
    assert catalog._identifiers({"rg-doi": "https://dx.doi.org/10.1000/example", "pmid-id": "11111111 and 22222222"}) == ("10.1000/example", None)
    with pytest.raises(ValueError, match="Unexpected DOI"):
        catalog._identifiers({"rg-doi": ["10.1000/invalid"]})


def test_frontmatter_handles_bom_and_reports_invalid_yaml(tmp_path):
    file = tmp_path / "index.qmd"
    file.write_text("\ufeff---\ntitle: Valid\n---\nUncopied body", encoding="utf-8")
    assert catalog._frontmatter(file)["title"] == "Valid"
    file.write_text("---\ntitle: [unterminated\n---\n", encoding="utf-8")
    with pytest.raises(Exception):
        catalog._frontmatter(file)
    file.write_text("---\n- not a mapping\n---\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing guideline title"):
        catalog._frontmatter(file)


def test_empty_published_tree_is_rejected(tmp_path):
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "empty"], check=True)
    with pytest.raises(ValueError, match="No published"):
        catalog.inventory(tmp_path)


def test_cli_round_trip_and_check_drift(tmp_path):
    import json
    import subprocess
    import sys

    source = tmp_path / "upstream"
    source.mkdir()
    subprocess.run(["git", "init", "-q", str(source)], check=True)
    page = source / "reporting-guidelines" / "trial" / "index.qmd"
    page.parent.mkdir(parents=True)
    page.write_text("---\ntitle: Trial\n---\nCopyrighted body not copied", encoding="utf-8")
    subprocess.run(["git", "-C", str(source), "add", "."], check=True)
    subprocess.run(["git", "-C", str(source), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "initial"], check=True)
    output = tmp_path / "catalogue.json"
    command = [sys.executable, str(SCRIPT), "--source", str(source), "--mode", "catalogue", "--output", str(output)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["guidelines"][0]["title"] == "Trial"
    assert "Copyrighted body" not in str(data)
    subprocess.run(command + ["--check"], check=True, capture_output=True, text=True)
    output.write_text("altered", encoding="utf-8")
    mismatch = subprocess.run(command + ["--check"], capture_output=True, text=True)
    assert mismatch.returncode != 0
    assert "differs from pinned source" in mismatch.stderr
