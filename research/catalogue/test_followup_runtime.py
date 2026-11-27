import numpy as np

from research.catalogue.followup import fit_predict


def test_classification_unknown_is_not_negative_and_no_unseen_labels():
    a = np.array([[1., 0.], [0., 1.], [1., 1.], [0., 1.]])
    b = np.array([[1., 0.], [0., 1.]])
    gold = [['A'], ['B'], [], ['B']]
    for method in ('knn', 'logistic', 'balanced'):
        ranking = fit_predict(a, b, gold, method)
        assert len(ranking) == 2 and ranking[0][0] == 'A' and ranking[1][0] == 'B'
        assert all(set(r) <= {'A', 'B'} for r in ranking)
    assert fit_predict(a, b, [[], [], [], []], 'balanced') == [[], []]


