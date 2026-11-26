from research.catalogue.vector_classification import groups, evaluate, design


def test_groups_conserve_identity_and_family():
    rows = [dict(id='a', acronym='PRISMA 2020', doi='x', title='Guideline A'),
            dict(id='b', acronym='PRISMA-P', title='Guideline B'),
            dict(id='c', pmid='3', doi='x', title='Guideline C'),
            dict(id='d', title='Distinct')]
    result = groups(rows)
    assert result[0] == result[1] == result[2]
    assert result[0] != result[3]


def test_metrics_distinguish_unknown_and_misses():
    rows = [{'gold': ['a', 'b'], 'ranking': ['a', 'c']}, {'gold': [], 'ranking': ['x']},
            {'gold': ['b'], 'ranking': []}]
    out = evaluate(rows)
    assert out['eligible'] == 2 and out['unknown'] == 1
    assert out['hits_at_3'] == 1 and out['positives'] == 3
    assert out['macro_recall_at_3'] == .25
    assert out['no_rank'] == 1
    assert len(design()) == 12


def test_facet_cooccurrence_does_not_treat_unspecified_as_absence():
    from research.catalogue.vector_classification import facet_associations

    rows = [dict(study_types=['A'], clinical_areas=['X'], report_sections=['Whole report']),
            dict(study_types=['A'], clinical_areas=['No clinical specialty specified']),
            dict(study_types=['B'], clinical_areas=['X'])]
    panel = facet_associations(rows)[0]
    assert panel['eligible'] == 2 and panel['missing_either'] == 1
    edge = panel['edges'][0]
    assert edge['count'] == 1 and edge['left_count'] == 1 and edge['right_count'] == 2
    assert edge['p_right_given_left'] == 1 and edge['p_left_given_right'] == .5
