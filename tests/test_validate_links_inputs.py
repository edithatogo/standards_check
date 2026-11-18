"""Unreadable and malformed sidecars must not hide other link failures."""

import pytest

from scripts import validate_links


@pytest.mark.parametrize("content", [
    b"\xff", b"source_url: [", b"- invalid-root", b"citation: invalid",
    b"source_url: 123", b"citation: {doi: 123}",
])
def test_bad_input_is_reported_and_other_files_continue(tmp_path, monkeypatch, content):
    invalid = tmp_path / "invalid.yml"
    invalid.write_bytes(content)
    valid = tmp_path / "valid.yml"
    valid.write_text("source_url: https://example.com/valid\n", encoding="utf-8")
    visited = []

    def validate(url, path):
        visited.append((url, path))
        return {"file": path, "url": url, "status": 404, "type": "BROKEN"}

    monkeypatch.setattr(validate_links, "validate_url", validate)
    broken, redirects, warnings = validate_links.check_links_in_files([str(invalid), str(valid)])
    assert len(broken) == 2
    assert broken[0]["type"] == "ERROR"
    assert broken[0]["file"] == str(invalid)
    assert broken[1]["status"] == 404
    assert visited == [("https://example.com/valid", str(valid))]
    assert redirects == warnings == []


def test_missing_file_is_an_error(tmp_path):
    tasks, errors = validate_links.process_file(str(tmp_path / "missing.yml"))
    assert tasks == []
    assert errors[0]["status"] == "INPUT_ERROR"


def test_null_citation_is_optional(tmp_path):
    path = tmp_path / "valid.yml"
    path.write_text("source_url: https://example.com/\ncitation: null\n", encoding="utf-8")
    assert validate_links.process_file(str(path)) == ([("https://example.com/", str(path))], [])
