from synthetic import fixture, spans, verify_anchor, rrf


def test_fixture_family_split_and_offsets():
    rows = fixture()
    assert len(rows) == 36
    assert len({r['family'] for r in rows}) == 6
    assert {r['family'] for r in rows if r['split'] == 'dev'} == {'PRISMA','CHEERS'}
    for row in rows:
        for side in ('doc','query'):
            assert set(spans(row, side)) == {'actor','condition','exception'}
            for role, (a,b) in spans(row,side).items():
                assert row[side][a:b] == row[role]


def test_anchor_and_fusion():
    assert verify_anchor('ABC', 0, 3, 'ABC')
    assert not verify_anchor('ABC', -1, 3, 'ABC')
    assert not verify_anchor('ABC', 1, 3, 'ABC')
    assert rrf(['b','a'],['a','c']) == ['a','b','c']


def test_layout_presence_does_not_claim_qualifier_linkage(tmp_path):
    from synthetic import layout

    result = layout(fixture(), tmp_path)
    assert result['qualifier_linkage_measured'] is False
    for arm in result['arms'].values():
        assert 'qualifier_links' not in arm
        assert arm['co_extracted_body_note_pairs'] == sum(r['body_and_note_present'] for r in arm['records'])
        assert all('linked' not in r for r in arm['records'])
        assert all(r['body_and_note_present'] == (r['body'] and r['footnote']) for r in arm['records'])
