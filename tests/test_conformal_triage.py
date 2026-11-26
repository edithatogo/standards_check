"""Synthetic rank and abstention tests; no empirical model qualification."""

import math
import unittest

from scripts.conformal_triage import prediction_set


class ConformalTriageTests(unittest.TestCase):
    def test_exact_rank_and_ties(self):
        calibration = [("equivalent", 0.25)] * 99
        result = prediction_set(
            calibration, {"equivalent": 0.25, "contradictory": 0.5}, alpha_basis_points=100
        )
        self.assertEqual(result.labels, ("equivalent",))
        self.assertEqual(result.candidate, "equivalent")
        self.assertEqual(result.underpowered_labels, ())

    def test_small_calibration_and_empty_calibration_abstain(self):
        scores = {"equivalent": 0.1, "contradictory": 0.9}
        for calibration in ([], [("equivalent", 0.1)] * 98):
            result = prediction_set(calibration, scores, alpha_basis_points=100)
            self.assertEqual(result.labels, ("contradictory", "equivalent"))
            self.assertEqual(result.underpowered_labels, result.labels)
            self.assertIsNone(result.candidate)

    def test_empty_and_multiple_sets_abstain(self):
        calibration = [("a", 0.25)] * 99
        for scores, expected in (({"b": 0.5, "a": 0.5}, ()), ({"b": 0.25, "a": 0.1}, ("a", "b"))):
            result = prediction_set(calibration, scores, alpha_basis_points=100)
            self.assertEqual(result.labels, expected)
            self.assertIsNone(result.candidate)

    def test_mondrian_uses_class_strata_and_holds_missing_strata(self):
        calibration = [("a", 0.2)] * 99 + [("b", 0.8)] * 99
        scores = {"a": 0.3, "b": 0.8}
        result = prediction_set(calibration, scores, alpha_basis_points=100, mondrian=True)
        self.assertEqual(result.candidate, "b")
        sparse = prediction_set(calibration[:99], scores, alpha_basis_points=100, mondrian=True)
        self.assertEqual(sparse.labels, ("b",))
        self.assertEqual(sparse.underpowered_labels, ("b",))
        self.assertIsNone(sparse.candidate)

    def test_invalid_scores_and_alpha_are_rejected(self):
        for alpha in (0, 10_000, -1, True, 1.5):
            with self.assertRaises(ValueError):
                prediction_set([], {"a": 0.1}, alpha_basis_points=alpha)
        for calibration, scores in (
            ([], {}),
            ([], {"": 0.1}),
            ([], {"a": math.inf}),
            ([], {"a": True}),
            ([("a", math.nan)], {"a": 0.1}),
            ([("a", False)], {"a": 0.1}),
            ([("unknown", 0.1)], {"a": 0.1}),
        ):
            with self.assertRaises(ValueError):
                prediction_set(calibration, scores, alpha_basis_points=100)

    def test_exhaustive_five_rank_example(self):
        values = [0.1, 0.2, 0.3, 0.4, 0.5]
        misses = 0
        for index, value in enumerate(values):
            calibration = [("a", score) for i, score in enumerate(values) if i != index]
            result = prediction_set(calibration, {"a": value, "b": 0.0}, alpha_basis_points=2000)
            misses += "a" not in result.labels
        self.assertEqual(misses, 1)
