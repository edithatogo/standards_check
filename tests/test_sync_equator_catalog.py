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
    with pytest.raises(ValueError, match="Unterminated"):
        catalog.build_catalog(tmp_path, SHA, files, metadata=True)
    page.write_text("---\ntitle: Valid\ncategories: invalid-scalar\n---\n")
    with pytest.raises(ValueError, match="Unexpected categories"):
        catalog.build_catalog(tmp_path, SHA, files, metadata=True)


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
