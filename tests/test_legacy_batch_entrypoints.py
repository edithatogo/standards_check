"""Real document bytes exercise retained batch entry points in an isolated directory."""

from pathlib import Path
import runpy

from docx import Document
import pytest

ROOT = Path(__file__).resolve().parents[1]


def make_document(path, text):
    document = Document()
    if text:
        document.add_paragraph(text)
    document.save(path)


@pytest.mark.parametrize(
    "script, suffix",
    [
        ("extract_all_docx.py", "-temp.md"),
        ("extract_and_convert.py", "-extracted.md"),
    ],
)
def test_batch_preserves_document_content_and_isolates_invalid_members(
    tmp_path, monkeypatch, capsys, script, suffix
):
    source = tmp_path / "docx/variants"
    source.mkdir(parents=True)
    make_document(source / "example.docx", "1. Report all outcomes.")
    make_document(source / "empty.docx", "")
    (source / "broken.docx").write_bytes(b"not a ZIP package")
    (source / "ignored.txt").write_text("ignored content")
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(ROOT / script), run_name="__main__")
    content = (tmp_path / f"example{suffix}").read_text()
    assert "Report all outcomes." in content
    assert "ignored content" not in content
    assert not (tmp_path / f"empty{suffix}").exists()
    assert not (tmp_path / f"broken{suffix}").exists()
    assert "Failed to extract content from broken.docx" in capsys.readouterr().out


@pytest.mark.parametrize(
    "script",
    [
        "extract_all_docx.py",
        "extract_and_convert.py",
        "extract_docx_content.py",
        "simple_extract.py",
    ],
)
def test_missing_source_directory_creates_no_derivative(tmp_path, monkeypatch, capsys, script):
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(ROOT / script), run_name="__main__")
    assert list(tmp_path.iterdir()) == []
    assert "not" in capsys.readouterr().out


@pytest.mark.parametrize("content", ["Report all outcomes.", "", None])
def test_named_document_entrypoint_preserves_text_or_records_extraction_failure(
    tmp_path, monkeypatch, capsys, content
):
    source = tmp_path / "docx/variants"
    source.mkdir(parents=True)
    path = source / "consort-cluster-crossover.docx"
    if content is None:
        path.write_bytes(b"invalid document")
    else:
        make_document(path, content)
    (source / "notes.txt").write_text("not a document")
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(ROOT / "extract_docx_content.py"), run_name="__main__")
    output = tmp_path / "consort-cluster-crossover-content.txt"
    if content:
        assert output.read_text() == content
    else:
        assert not output.exists()
        assert "Failed to extract content" in capsys.readouterr().out


def test_extraction_plan_lists_only_docx_candidates(tmp_path, monkeypatch):
    source = tmp_path / "docx/variants"
    source.mkdir(parents=True)
    (source / "candidate.docx").write_bytes(b"not evaluated during discovery")
    (source / "notes.txt").write_text("not a candidate")
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(ROOT / "simple_extract.py"), run_name="__main__")
    plan = (tmp_path / "extraction_plan.txt").read_text()
    assert "candidate.docx" in plan
    assert "notes.txt" not in plan
    assert "not evaluated" not in plan
