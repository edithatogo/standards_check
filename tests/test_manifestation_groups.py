import hashlib
import pytest
from scripts.compare_guideline_formats import manifestation_groups


def source(path, byte, ids, texts, issues=()):
    return {
        'path': path, 'source_sha256': hashlib.sha256(byte.encode()).hexdigest(),
        'rows': [{'item_id': ident, 'identifier_anchor': f'{path}/id/{i}',
                  'requirement_anchor': f'{path}/text/{i}',
                  'requirement_sha256': hashlib.sha256(text.encode()).hexdigest()}
                 for i, (ident, text) in enumerate(zip(ids, texts, strict=True))],
        'issues': list(issues),
    }


def test_groups_preserve_aliases_and_hold_incomplete_or_unanchored():
    a = source('a.pdf', 'file a', ['1','2'], ['a','b'])
    b = source('a-copy.pdf', 'file a', ['1','2'], ['a','b'])
    c = source('c.docx', 'file c', ['1','2'], ['a','b'], ['non_body_parts_not_extracted'])
    d = source('different.docx', 'file d', ['1','2'], ['a','not b'])
    e = source('truncated.csv', 'file e', ['1'], ['a'])
    f = source('missing-anchor.csv', 'file f', ['1','2'], ['a','b'])
    f['rows'][1]['requirement_anchor'] = None
    g = source('reordered.csv', 'file g', ['2','1'], ['b','a'])
    result = manifestation_groups([a,b,c,d,e,f,g], ['1','2'])
    assert result['byte_alias_groups'][0]['paths'] == ['a-copy.pdf','a.pdf']
    assert sorted(result['ordered_row_hash_groups'][0]['paths']) == ['a-copy.pdf','a.pdf','c.docx']
    assert result['ordered_row_hash_groups'][0]['structural_holds'] == {'c.docx':['non_body_parts_not_extracted']}
    assert result['held_row_fingerprint_paths'] == ['missing-anchor.csv','reordered.csv','truncated.csv']
    assert result['independent_identity_verified'] is False
    assert result['canonical_admission'] is False


def test_no_reference_never_implies_content_group():
    a = source('a.pdf','same',['1'],['a']); b = source('b.pdf','same',['1'],['a'])
    result = manifestation_groups([a,b], [])
    assert len(result['byte_alias_groups']) == 1
    assert result['ordered_row_hash_groups'] == []
    assert result['held_row_fingerprint_paths'] == ['a.pdf','b.pdf']


def test_missing_bytes_not_same_and_duplicate_reference_rejected():
    a = source('a','one',['1'],['a']); a['source_sha256'] = None
    b = source('b','two',['1'],['a']); b['source_sha256'] = None
    result = manifestation_groups([a,b], ['1'])
    assert result['byte_alias_groups'] == []
    assert result['ordered_row_hash_groups'] == []
    assert result['held_row_fingerprint_paths'] == ['a','b']


def test_duplicate_paths_and_denominator_rejected():
    a = source('a','one',['1'],['a'])
    with pytest.raises(ValueError, match='duplicate manifestation path'):
        manifestation_groups([a,a], ['1'])
    with pytest.raises(ValueError, match='duplicate manifestation denominator'):
        manifestation_groups([a], ['1','1'])
