from research.catalogue.tool_selection import dominates, frontier, crosswalk_coverage


def test_noncompensatory_frontier_and_missing_cost():
    a = dict(recall=.8, precision=.6, macro_label_recall=.5, seconds=2)
    b = dict(recall=.7, precision=.6, macro_label_recall=.4, seconds=3)
    assert dominates(a,b)
    assert not dominates(b,a)
    out = frontier({'a':a, 'b':b, 'unmeasured':{**a, 'seconds':None}})
    assert out == {'pareto':['a'], 'unmeasured':['unmeasured']}


def test_crosswalk_does_not_promote_or_invent_unmapped_labels():
    cat = {'guidelines':[{'study_types':['Trials','Unknown'], 'clinical_areas':[], 'report_sections':[]}]}
    out = crosswalk_coverage(cat, {'study_types':{'Trials':['D002986']}})
    assert out['study_types']['mapped_labels'] == 1
    assert out['study_types']['unmapped_labels'] == ['Unknown']
    assert out['study_types']['admission'] == 'candidate_only'
