import hashlib
import pytest
from scripts import equator_literal_rows as e


def test_tripod_scope_and_note_links_are_separate():
    data = ['Methods', ['Topic', '1', 'D;E', 'Report result<sup>2</sup>.'],
            ['', '2', 'E', 'Report analysis.']]
    result = e.priority_literal_metadata(data, 'tripod', ['1','2'])
    assert result['expected_order'] is True
    assert result['rows'][0]['scope'] == 'D;E'
    assert result['rows'][0]['scope_anchor'] == 'ROWS/1/2'
    assert result['rows'][0]['note_references'] == ['2']
    assert result['rows'][1]['topic_anchor'] == 'ROWS/1/0'
    assert 'Report result' not in str(result)
    with pytest.raises(ValueError):
        e.priority_literal_metadata(['Methods',['Topic','1','D or E','X']], 'tripod', ['1'])


def test_strobe_parent_star_and_subitems_are_not_flattened():
    data = ['Methods',['Participants','6*',False,[['6a','<em>Cohort</em> A'],['6b','B']]]]
    result = e.priority_literal_metadata(data, 'strobe', ['6'])
    row = result['rows'][0]
    assert row['printed_id']=='6*' and row['item_id']=='6'
    assert row['starred'] is True
    assert [x['item_id'] for x in row['subitems']] == ['6a','6b']
    assert row['subitems'][0]['requirement_anchor']=='ROWS/1/3/0/1'
    assert result['expected_order']
    assert 'Cohort' not in str(result)
    with pytest.raises(ValueError):
        e.priority_literal_metadata(['Methods',['Participants','6',False,[['7a','A']]]], 'strobe', ['6'])


def test_issuer_file_identity_not_inferred_from_extension(tmp_path):
    p = tmp_path / 'issuer.pdf'
    p.write_bytes(b'%PDF-1.7\nsynthetic')
    raw = p.read_bytes()
    pin = hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw, usedforsecurity=False).hexdigest()
    assert e.issuer_pdf_identity(p,pin)['same_bytes_as_equator_pin'] is True
    assert e.issuer_pdf_identity(p,'a'*40)['same_bytes_as_equator_pin'] is False
    p.write_bytes(b'<html>not pdf</html>')
    with pytest.raises(ValueError):
        e.issuer_pdf_identity(p,pin)


def test_strobe_initial_ungrouped_title_row():
    result = e.priority_literal_metadata(
        [['Title', '1', True, [['1a', 'A'], ['1b', 'B']]], 'Methods',
         ['Study', '2', False, [['2', 'C']]]], 'strobe', ['1', '2']
    )
    assert result['expected_order']
    assert result['rows'][0]['section_anchor'] is None
    assert result['rows'][1]['section_anchor'] == 'ROWS/1'


def test_priority_receipt_keeps_missing_assets_and_exact_source_pins(tmp_path, monkeypatch):
    import json
    import sys

    data = ['Methods', ['Topic', '1', 'D', 'Report result.']]
    raw = ('const ROWS = ' + json.dumps(data) + ';\n').encode()
    qmd = tmp_path / 'tripod.qmd'
    qmd.write_bytes(raw)
    docx = tmp_path / 'tripod.docx'
    docx.write_bytes(b'synthetic DOCX')
    pdf = tmp_path / 'tripod.issuer.pdf'
    pdf.write_bytes(b'%PDF-1.7\nsynthetic')
    def blob(path):
        value = path.read_bytes()
        return hashlib.sha1(f'blob {len(value)}\0'.encode() + value, usedforsecurity=False).hexdigest()
    pins = ('tripod-ai-2024', blob(qmd), blob(docx), blob(pdf))
    spec = {'edition':'tripod-ai-2024', 'doi':'10.1000/example', 'table_item_ids':[['1']]}
    monkeypatch.setattr(e, 'compare_docx', lambda raw, name, refs, expected: {'comparison':{'compared':len(refs)}, 'issues':[]})
    result = e.observe_priority(tmp_path,'tripod',spec,pins)
    assert result['literal']['expected_order'] is True
    assert result['docx']['comparison']['compared'] == 1
    assert result['issuer_pdf']['same_bytes_as_equator_pin'] is True
    assert result['public_redistribution_qualified'] is False
    docx.unlink(); pdf.unlink()
    held = e.observe_priority(tmp_path,'tripod',spec,pins)
    assert held['literal']['expected_order'] is True
    assert held['docx']['error_type'] == 'FileNotFoundError'
    assert held['issuer_pdf']['error_type'] == 'FileNotFoundError'
    qmd.unlink()
    assert e.observe_priority(tmp_path,'tripod',spec,pins)['literal']['status'] == 'held'
    qmd.write_bytes(raw)
    specs = tmp_path / 'source/official/priority-article-candidates.json'
    specs.parent.mkdir(parents=True)
    specs.write_text(json.dumps([spec]))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(e,'PRIORITY_PINS',{'tripod':pins})
    out = tmp_path / 'out.json'
    monkeypatch.setattr(sys,'argv',['reader','--source-dir',str(tmp_path),'--output',str(out),'--priority'])
    e.main()
    assert json.loads(out.read_text())['editions'][0]['literal']['expected_order']


def test_priority_dialect_rejects_unbound_duplicate_or_invalid_inputs():
    for data,name,expected in [([], 'unknown',['1']), ([], 'tripod',[]),
        (['Methods',['','1','E','A']], 'tripod',['1']),
        (['Methods',['T','1','E','']], 'tripod',['1']),
        (['Methods',['T','x','E','A']], 'tripod',['1']),
        (['Methods',['T','1','bad',[['1','A']]]], 'strobe',['1']),
        (['Methods',['T','1',True,[['1','A'],['1','B']]]], 'strobe',['1'])]:
        with pytest.raises(ValueError):
            e.priority_literal_metadata(data,name,expected)
