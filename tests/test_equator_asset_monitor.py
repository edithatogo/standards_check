from scripts import sync_equator_catalog as catalog
import subprocess
import json
import pytest


def test_asset_drift_without_index_change(tmp_path):
    def git(*args):
        return subprocess.run(['git', '-C', str(tmp_path), *args], check=True, text=True, capture_output=True).stdout.strip()
    git('init', '-q')
    git('config', 'user.name', 'Test')
    git('config', 'user.email', 'test@example.invalid')
    root = tmp_path / 'reporting-guidelines'
    page = root / 'trial'
    page.mkdir(parents=True)
    (page / 'index.qmd').write_text('---\ntitle: Trial\n---\n')
    (page / 'checklist.pdf').write_text('private-like synthetic source text')
    (page / 'old.docx').write_text('old')
    (page / 'old.docx').chmod(0o755)
    generated = page / 'checklist_files'
    generated.mkdir()
    (generated / 'generated.html').write_text('ignore generated')
    dev = root / 'under-development'
    dev.mkdir()
    (dev / 'index.qmd').write_text('---\ntitle: Draft\n---\n')
    git('add', '.'); git('commit', '-qm', 'initial')
    rev, pages = catalog.inventory(tmp_path)
    one = catalog.asset_report(tmp_path, rev, pages)
    assert one['changes'] is None
    assert one['published_count'] == 1
    assert len(one['assets']) == 3
    assert 'private-like' not in json.dumps(one)
    (page / 'checklist.pdf').write_text('changed')
    (page / 'old.docx').unlink()
    (page / 'new checklist.docx').write_text('new')
    git('add', '-A'); git('commit', '-qm', 'asset-only changes')
    rev2, pages2 = catalog.inventory(tmp_path)
    assert pages2 == pages
    two = catalog.asset_report(tmp_path, rev2, pages2, one)
    assert two['previous_source_revision'] == rev
    assert two['changes']['added'] == ['reporting-guidelines/trial/new checklist.docx']
    assert two['changes']['removed'] == ['reporting-guidelines/trial/old.docx']
    assert two['changes']['revised'] == ['reporting-guidelines/trial/checklist.pdf']
    assert two['assets']['reporting-guidelines/trial/checklist.pdf'] != one['assets']['reporting-guidelines/trial/checklist.pdf']
    with pytest.raises(ValueError, match='asset baseline'):
        catalog.asset_report(tmp_path, rev2, pages2, {**one, 'source_repository': 'wrong'})
    with pytest.raises(ValueError, match='asset baseline'):
        catalog.asset_report(tmp_path, rev2, pages2, {**one, 'assets': {'other': 'fake'}})


def test_asset_cli_preserves_baseline_and_legacy_modes(tmp_path, monkeypatch):
    import sys

    repo = tmp_path / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    page = repo / 'reporting-guidelines' / 'test' / 'index.qmd'
    page.parent.mkdir(parents=True)
    page.write_text('---\ntitle: Test\n---\n')
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'init'], check=True)
    baseline, out = tmp_path / 'baseline.json', tmp_path / 'out.json'
    argv = ['sync', '--source', str(repo), '--mode', 'assets', '--output', str(baseline)]
    monkeypatch.setattr(sys, 'argv', argv)
    catalog.main()
    old = baseline.read_bytes()
    assert json.loads(old)['changes'] is None
    monkeypatch.setattr(sys, 'argv', argv[:-1] + [str(out), '--previous-assets', str(baseline)])
    catalog.main()
    assert json.loads(out.read_text())['changes'] == {'added': [], 'removed': [], 'revised': []}
    assert baseline.read_bytes() == old
    monkeypatch.setattr(sys, 'argv', ['sync', '--source', str(repo), '--mode', 'discover', '--output', str(out), '--previous-assets', str(baseline)])
    with pytest.raises(SystemExit):
        catalog.main()
