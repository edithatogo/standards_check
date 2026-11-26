from scripts import equator_literal_rows as e
from scripts.structured_source import fingerprint


def test_projection_preserves_markers_and_link_targets_separately():
    text = 'Report [[named source|path.pdf]]<sup>2</sup> and 95% CI.'
    result = e.priority_display_fields(text)
    assert result['display_content_sha256'] == fingerprint('Report named source and 95% CI.')
    assert result['note_references'] == ['2']
    assert result['link_target_sha256'] == [fingerprint('path.pdf')]
    changed = e.priority_display_fields(text.replace('path.pdf', 'other.pdf'))
    assert changed['display_content_sha256'] == result['display_content_sha256']
    assert changed['link_target_sha256'] != result['link_target_sha256']
    assert e.priority_display_fields('Report 2 and 95% CI.')['display_content_sha256'] != result['display_content_sha256']
    assert e.priority_display_fields('2<sup>x</sup>')['display_content_sha256'] == fingerprint('2<sup>x</sup>')


def test_tripod_scope_uses_only_cell_between_id_and_requirement():
    rows = [{'item_id': '1', 'scope': 'E'}, {'item_id': '2', 'scope': 'D;E'}, {'item_id': '3', 'scope': 'D'}]
    def observed(item, idx, cells):
        return {'item_id': item, 'status':'observed_not_qualified', 'row_anchor': f'body/2/r{idx}',
                'identifier_anchor':f'body/2/r{idx}/c2','requirement_anchor':f'body/2/r{idx}/c4',
                'other_cells':[{'anchor':f'body/2/r{idx}/c{col}','text_sha256':fingerprint(text)} for col,text in cells]}
    observations = [observed('1',1,[(1,'D'),(3,'E')]), observed('2',2,[(1,'D;E'),(3,'D')])]
    result=e.tripod_scope_comparison(rows, observations)
    assert [r['status'] for r in result] == ['equal','different','unknown']
    assert result[0]['scope_anchor'] == 'body/2/r1/c3'
    observations.append(observations[0])
    assert e.tripod_scope_comparison(rows, observations)[0]['status'] == 'unknown'


def test_strobe_candidates_preserve_star_and_do_not_certify_numeric_cells():
    ref=[{'item_id':'8','printed_id':'8*'}, {'item_id':'13','printed_id':'13*'}]
    def row(idx, values):
        return {'anchor':f'body/2/r{idx}', 'cells':[{'anchor':f'body/2/r{idx}/c{i}', 'column':i, 'text_sha256':fingerprint(s)} for i,s in enumerate(values,1)]}
    structure={'blocks':[{'rows':[row(1,['Methods','8*','text']),row(2,['Results','13*','13*'])]}]}
    candidates=e.strobe_identifier_candidates(structure,ref)
    assert [x['printed_id'] for x in candidates]==['8*','13*','13*']
    assert [x['cell_anchor'] for x in candidates]==['body/2/r1/c2','body/2/r2/c2','body/2/r2/c3']
    assert all(x['status']=='unverified_cell_candidate' for x in candidates)
