import copy

import pytest

from research.publication.structural_recovery import topic_context


def edition():
    rows = [{'item_id': '1a', 'topic_anchor': 'q1'}, {'item_id': '1b', 'topic_anchor': 'q1'}]
    return {'edition': 'demo', 'expected_ids': ['1a', '1b'], 'status': 'held',
            'literal': {'rows': rows, 'groups': [{'anchor': 'q1', 'kind': 'topic', 'text_sha256': 'a'}]},
            'docx': {'anchor_evidence': [
                {'item_id': '1a', 'row_anchor': 'r1', 'other_cells': [{'anchor': 'r1/c1', 'text_sha256': 'a', 'merge_origin': 'r1/c1', 'origin_text_sha256': 'a'}]},
                {'item_id': '1b', 'row_anchor': 'r2', 'other_cells': [{'anchor': 'r2/c1', 'text_sha256': 'empty', 'merge_origin': 'r1/c1', 'origin_text_sha256': 'a'}]},
            ]}}


def test_resolves_actual_origin_and_conserves_rows():
    r = topic_context(edition())
    assert r['n'] == 2 and r['direct'] == 1 and r['closure'] == 2
    assert r['gained'] == 1 and r['lost'] == 0 and r['source_status'] == 'held'


def test_rejects_forged_origin_and_nonconserved_ids():
    broken = edition()
    broken['docx']['anchor_evidence'][1]['other_cells'][0]['origin_text_sha256'] = 'wrong'
    with pytest.raises(ValueError, match='origin'):
        topic_context(broken)
    broken = copy.deepcopy(edition())
    broken['literal']['rows'].pop()
    with pytest.raises(ValueError, match='identity'):
        topic_context(broken)
