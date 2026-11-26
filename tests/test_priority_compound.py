from scripts import equator_literal_rows as e
from scripts.structured_source import fingerprint


def test_explicit_note_marker_projection_and_unbound_digits():
    ref = {'item_id': '23b', 'requirement_anchor': 'ROWS/1/3',
           **e.priority_display_fields('Report if relevant<sup>3</sup>.')}
    row = {'item_id': '23b', 'identifier_anchor': 'body/1/r1/c2',
           'requirement_anchor': 'body/1/r1/c4', 'requirement_sha256': fingerprint('Report if relevant3.')}
    result = e.tripod_marker_comparison([ref], [row], ['23b'])
    assert result[0]['status'] == 'explicit_marker_content_equal'
    assert result[0]['note_references'] == ['3']
    assert result[0]['note_linkage_qualified'] is False
    assert e.tripod_marker_comparison([ref], [row, row], ['23b'])[0]['status'] == 'held'
    assert e.tripod_marker_comparison([ref], [{**row, 'requirement_anchor': None}], ['23b'])[0]['status'] == 'held'
    plain = {**ref, **e.priority_display_fields('Report if relevant.')}
    assert e.tripod_marker_comparison([plain], [row], ['23b'])[0]['status'] == 'held'
    stripped = {**row, 'requirement_sha256': fingerprint('Report if relevant.')}
    assert e.tripod_marker_comparison([ref], [stripped], ['23b'])[0]['status'] == 'display_content_equal'


def cell(anchor, col, text, merge=None, origin=None):
    return {'anchor': f'{anchor}/c{col}', 'column': col, 'colspan': 1,
            'vertical_merge': merge, 'merge_origin': origin,
            'empty': not text, 'text_sha256': fingerprint(text)}


def row(anchor, printed, text, merge=None, origin=None):
    return {'anchor': anchor, 'cells': [cell(anchor, 1, 'Topic'),
            cell(anchor, 2, printed, merge, origin), cell(anchor, 3, text),
            cell(anchor, 4, '8*')]}


def reference():
    return [{'item_id': '8', 'printed_id': '8*', 'subitems': [
        {'item_id': '8a', 'requirement_anchor': 'ROWS/1/3/0/1',
         'display_content_sha256': fingerprint('(a) Report A')},
        {'item_id': '8b', 'requirement_anchor': 'ROWS/1/3/1/1',
         'display_content_sha256': fingerprint('(b) Report B')}]}]


def test_compound_group_requires_explicit_merge_and_preserves_star():
    first = row('body/3/r2', '8*', '(a) Report A', 'restart', 'body/3/r2/c2')
    second = row('body/3/r3', '', '(b) Report B', 'continue', 'body/3/r2/c2')
    table = {'anchor': 'body/3', 'grid_width': 4, 'rows': [first, second]}
    result = e.strobe_compound_comparison({'blocks': [table]}, reference())[0]
    assert result['status'] == 'candidate_content_matches'
    assert result['printed_id'] == '8*'
    assert result['note_linkage_qualified'] is False
    assert [p['requirement_anchor'] for p in result['pairs']] == ['body/3/r2/c3', 'body/3/r3/c3']
    assert result['pairs'][1]['identifier_merge_origin'] == 'body/3/r2/c2'
    # A neighbouring row or a score-column ID cannot be silently bound.
    bad = row('body/3/r3', '', '(b) Report B')
    assert e.strobe_compound_comparison({'blocks': [{**table, 'rows':[first,bad]}]}, reference())[0]['status'] == 'held'
    # No continuation across table boundaries, even with a forged origin.
    assert e.strobe_compound_comparison({'blocks': [{**table,'rows':[first]}, {**table,'anchor':'body/5','rows':[second]}]}, reference())[0]['status'] == 'held'
    # A repeated printed ID is ambiguous, not two observations.
    duplicate = row('body/3/r4', '8*', '(a) Report A')
    assert e.strobe_compound_comparison({'blocks': [{**table,'rows':[first,second,duplicate]}]}, reference())[0]['status'] == 'held'


def test_compound_group_preserves_mismatch_and_ignores_wrong_column():
    first = row('body/3/r2', '8*', '(a) Report A', 'restart', 'body/3/r2/c2')
    second = row('body/3/r3', '', '(b) Do not report B', 'continue', 'body/3/r2/c2')
    result = e.strobe_compound_comparison({'blocks':[{'anchor':'body/3','grid_width':4,'rows':[first,second]}]}, reference())[0]
    assert result['status'] == 'held'
    assert [p['equal'] for p in result['pairs']] == [True, False]
    assert len(result['candidate_groups']) == 1
    first['cells'][1] = cell('body/3/r2',2,'other')
    result = e.strobe_compound_comparison({'blocks':[{'anchor':'body/3','grid_width':4,'rows':[first]}]}, reference())[0]
    assert result['status'] == 'held'
    assert result['candidate_groups'] == []
