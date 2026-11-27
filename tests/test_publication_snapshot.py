import csv
import hashlib
import json
import zipfile

import pytest

from research.publication.compile_snapshot import compile_snapshot, select


def test_selector():
    assert list(select({'a': {'x': 3, 'y': 4}}, 'a/*')) == [('x', 3), ('y', 4)]
    with pytest.raises(KeyError):
        list(select({'a': {}}, 'a/missing'))


def test_snapshot_reproducible_and_digest_bound(tmp_path):
    source = tmp_path / 'x.json'
    source.write_text(json.dumps({'arms': {'a': {'n': 3, 'correct': 2, 'unknown': None}}}))
    manifest = tmp_path / 'inputs.tsv'
    manifest.write_text('file\tsha256\trun_id\tartifact_id\n' + f'x.json\t{hashlib.sha256(source.read_bytes()).hexdigest()}\t\t\n')
    spec = tmp_path / 'panels.tsv'
    spec.write_text('panel\tfile\tmember\tselector\tmetrics\tunit\tdenominator\treference\n'
                    'demo\tx.json\t\tarms/*\tcorrect;unknown\tcase\t@n\tsynthetic\n')
    first = compile_snapshot(tmp_path, manifest, spec, tmp_path / 'out')
    second = compile_snapshot(tmp_path, manifest, spec, tmp_path / 'out')
    assert first == second
    rows = list(csv.DictReader((first / 'comparison.tsv').open(), delimiter='\t'))
    assert [(r['metric'], r['value'], r['denominator']) for r in rows] == [('correct', '2', '3'), ('unknown', '', '3')]
    with zipfile.ZipFile(first / 'evidence.zip') as z:
        assert z.read('raw/x.json') == source.read_bytes()
    source.write_text('{}')
    with pytest.raises(ValueError, match='digest'):
        compile_snapshot(tmp_path, manifest, spec, tmp_path / 'out')


def test_new_projection_creates_new_version_and_preserves_prior(tmp_path):
    source = tmp_path / 'x.json'
    source.write_text('{"n": 3, "correct": 2, "errors": 1}')
    manifest = tmp_path / 'inputs.tsv'
    manifest.write_text('file\tsha256\trun_id\tartifact_id\n' + f'x.json\t{hashlib.sha256(source.read_bytes()).hexdigest()}\t\t\n')
    spec = tmp_path / 'panels.tsv'
    header = 'panel\tfile\tmember\tselector\tmetrics\tunit\tdenominator\treference\n'
    spec.write_text(header + 'demo\tx.json\t\t\tcorrect\tcase\t@n\tsynthetic\n')
    first = compile_snapshot(tmp_path, manifest, spec, tmp_path / 'out')
    original = (first / 'comparison.tsv').read_bytes()
    spec.write_text(header + 'demo\tx.json\t\t\tcorrect;errors\tcase\t@n\tsynthetic\n')
    second = compile_snapshot(tmp_path, manifest, spec, tmp_path / 'out')
    assert first != second
    assert (first / 'comparison.tsv').read_bytes() == original
    (second / 'comparison.tsv').write_text('tampered')
    with pytest.raises(ValueError, match='collision'):
        compile_snapshot(tmp_path, manifest, spec, tmp_path / 'out')
