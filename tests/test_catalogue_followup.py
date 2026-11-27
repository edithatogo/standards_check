import pytest

from research.catalogue.followup import role, paired, validate_folds


def test_context_roles_do_not_turn_development_method_into_target():
    assert role('Guideline for reporting clinical trials: a systematic review', 24, 39) == 'target_candidate'
    s = 'Reporting guideline for clinical trials developed using a systematic review'
    i = s.index('systematic review')
    assert role(s, i, i + len('systematic review')) == 'development_candidate'
    s = 'A systematic review of reporting guidelines for clinical trials'
    i = s.index('systematic review')
    assert role(s, i, i + len('systematic review')) == 'unresolved'
    s = 'Guidelines for reporting clinical trials except non-randomized trials'
    i = s.index('non-randomized')
    assert role(s, i, len(s)) == 'unresolved'
    with pytest.raises(ValueError):
        role('abc', 1, 4)


def test_fold_rejects_family_leak_and_missing_ids():
    rows = [dict(id='a', title='X', acronym='CONSORT'), dict(id='b', title='Y', acronym='CONSORT'), dict(id='c', title='Z')]
    with pytest.raises(ValueError, match='group'):
        validate_folds(rows, [['a'], ['b', 'c']])
    with pytest.raises(ValueError, match='coverage'):
        validate_folds(rows, [['a','b']])
    assert len(validate_folds(rows, [['a','b'],['c']])) == 2


def test_paired_positive_gains_losses_and_unknown():
    a = [{'id':'a','gold':['x','y'],'ranking':['x']},{'id':'b','gold':[],'ranking':['y']}]
    b = [{'id':'a','gold':['x','y'],'ranking':['y']},{'id':'b','gold':[],'ranking':[]}]
    assert paired(a,b) == {'shared':0,'gains':1,'losses':1,'missed_both':0}
    with pytest.raises(ValueError,match='identity'):
        paired(a,b[:1])


def test_dense_matrix_rejects_zero_nonfinite_and_wrong_coverage():
    from research.catalogue.followup import embed_titles
    rows = [{'id':'a','title':'A'}, {'id':'b','title':'B'}, {'id':'z'}]
    seen = []
    def fake(s):
        seen.append(s)
        return [1., 2.] if s == 'A' else [2., 1.]
    vectors, receipt = embed_titles(rows, fake, 2)
    assert seen == ['A','B'] and vectors.shape == (2,2) and receipt['requests'] == 2
    assert receipt['ids'] == ['a','b']
    for invalid in ([0.,0.],[1.,float('nan')],[1.]):
        with pytest.raises(ValueError,match='embedding'):
            embed_titles(rows, lambda _: invalid, 2)


def test_fixed_assignment_conserves_fold_ids():
    from research.catalogue.followup import decode_fold_assignment
    rows = [dict(id='a', title='X'),dict(id='b', title='Y'),dict(id='c', title='Z')]
    assert decode_fold_assignment(rows,'010',2) == [['a','c'],['b']]
    for bad in ('01','012','000'):
        with pytest.raises(ValueError,match='assignment'):
            decode_fold_assignment(rows,bad,2)
