import copy
import hashlib

import pytest

from research.catalogue.ontology_projection import project, mentions, hierarchy


ROOT = {'id': 'D001185', 'label': 'Artificial Intelligence', 'trees': ['G17.035.250'],
        'aliases': ['artificial intelligence'], 'category': 'Artificial intelligence/Machine learning'}
CHILD = {'id': 'D000069550', 'label': 'Machine Learning', 'trees': ['G17.035.250.500'],
         'aliases': ['machine learning'], 'category': 'Artificial intelligence/Machine learning'}


def fixture():
    return {'source_revision': 'a'*40, 'published_count': 2, 'guidelines': [
        {'id': 'equator:a', 'source_blob_sha': 'b'*40, 'title': 'Machine learning in clinical studies',
         'metadata_status': 'extracted_unverified', 'study_types': ['No study design specified'],
         'clinical_areas': ['No clinical specialty specified'], 'report_sections': ['Whole report']},
        {'id': 'equator:b', 'source_blob_sha': 'c'*40, 'title': None,
         'metadata_status': 'needs_review', 'study_types': None, 'clinical_areas': None, 'report_sections': None}]}


def test_project_preserves_all_entries_and_separates_mentions_from_declared_facets():
    result = project(fixture(), [ROOT, CHILD])
    assert result['summary']['directory_entries'] == 2
    assert result['summary']['title_matched'] == 1
    assert result['summary']['title_missing'] == 1
    assert result['summary']['study_types_null'] == 1
    assert result['summary']['unspecified_design_with_candidate'] == 1
    assert result['summary']['facets']['study_types']['No study design specified'] == 1
    assert result['summary']['topic_counts']['D001185']['title_direct'] == 0
    assert result['summary']['topic_counts']['D001185']['title_with_ancestors'] == 1
    assert result['summary']['unverified_category_candidates'] == 1
    assert result['summary']['canonical_packs_promoted'] == 0
    edge = next(e for e in result['edges'] if e['predicate'] == 'title_mention_candidate')
    assert edge['start'] == 0 and edge['end'] == 16
    assert edge['span_sha256'] == hashlib.sha256(b'Machine learning').hexdigest()
    assert 'text' not in edge
    assert not any(e['predicate'] == 'equivalent' for e in result['edges'])
    ids = {n['id'] for n in result['nodes']}
    assert all(e['source'] in ids and e['target'] in ids for e in result['edges'])


def test_word_boundaries_and_negated_prefix_and_nested_matches():
    terms = [{'id': 'D1', 'aliases': ['randomized controlled trial', 'randomized controlled trials']},
             {'id': 'D2', 'aliases': ['non-randomized controlled trials']},
             {'id': 'D3', 'aliases': ['meta-analysis']},
             {'id': 'D4', 'aliases': ['network meta-analysis']}]
    out = mentions('Non-randomized controlled trials and network meta-analysis; metanalysis', terms)
    assert [m['concept'] for m in out] == ['D2', 'D4']
    assert mentions('xmeta-analysis', terms) == []


def test_bad_identity_missing_facet_and_invalid_tree_hold():
    d = fixture()
    d['guidelines'][1]['id'] = d['guidelines'][0]['id']
    with pytest.raises(ValueError, match='identity'):
        project(d, [ROOT, CHILD])
    d = fixture()
    d['guidelines'][0]['study_types'] = 'Clinical trials'
    with pytest.raises(ValueError, match='facet'):
        project(d, [ROOT, CHILD])
    broken = copy.deepcopy(CHILD)
    broken['trees'] = ['G17.035.2500']
    assert hierarchy([ROOT, broken]) == []
    with pytest.raises(ValueError, match='concept'):
        project(fixture(), [ROOT, ROOT])


def test_pack_gate_and_item_anchor_preserved():
    pack = {'pack_id': 'demo', 'version': '1', 'rights': {'status': 'cleared'},
            'verification': {'status': 'source_reconciled'}, 'requirements': [
                {'id': 'demo:1', 'source_anchor': 'row1', 'verbatim_text': 'Describe machine learning',
                 'rights': {'inherit_from_pack': True}}]}
    report = project(fixture(), [ROOT, CHILD], pack)
    assert report['summary']['requirement_items'] == 1
    assert report['summary']['requirement_matched'] == 1
    e = next(e for e in report['edges'] if e['predicate'] == 'requirement_mention_candidate')
    assert e['source_anchor'] == 'row1' and e['start'] == 9
    pack['rights']['status'] = 'held'
    with pytest.raises(ValueError, match='rights'):
        project(fixture(), [ROOT, CHILD], pack)


def test_ambiguous_alias_fails_closed():
    broken = copy.deepcopy(CHILD)
    broken['aliases'] = ROOT['aliases']
    with pytest.raises(ValueError, match='ambiguous'):
        project(fixture(), [ROOT, broken])
