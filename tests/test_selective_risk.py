import unittest

from scripts.selective_risk import evaluate


def rows(prefix, n):
    return [
        {"id": f"{prefix}-{i}-{j}", "family": f"{prefix}-{i}", "score_bps": score,
         "equivalent_candidate": True, "reference_equivalent": truth}
        for i in range(n) for j, (score, truth) in enumerate(((9000, True), (6000, False)))
    ]


class RiskTests(unittest.TestCase):
    def test_selects_only_on_calibration_and_counts_families(self):
        calibration = rows("c", 100)
        evaluation = rows("e", 30)
        evaluation[0]["reference_equivalent"] = False
        result = evaluate(calibration, evaluation, [5000, 8000], risk_limit_bps=500)
        self.assertEqual(result["selected_threshold_bps"], 8000)
        self.assertEqual(result["evaluation"]["accepted_families"], 30)
        self.assertEqual(result["evaluation"]["error_families"], 1)
        self.assertEqual(result["calibration"][0]["error_families"], 100)
        self.assertEqual(result["calibration"][1]["accepted_families"], 100)
        self.assertEqual(result["calibration"][1]["false_equivalences"], 0)

    def test_empty_and_underpowered_hold(self):
        result = evaluate(rows("c", 2), rows("e", 2), [10000], risk_limit_bps=100)
        self.assertIsNone(result["selected_threshold_bps"])
        self.assertIsNone(result["calibration"][0]["upper_family_risk"])
        result = evaluate(rows("c", 2), rows("e", 2), [8000], risk_limit_bps=100)
        self.assertIsNone(result["selected_threshold_bps"])

    def test_family_and_case_overlap_and_bad_grid_fail(self):
        calibration, evaluation = rows("c", 2), rows("e", 2)
        for thresholds in ([], [100, 100], [True], [10001]):
            with self.assertRaises(ValueError):
                evaluate(calibration, evaluation, thresholds)
        with self.assertRaises(ValueError):
            evaluate(calibration, calibration, [8000])
        evaluation[0]["family"] = calibration[0]["family"]
        with self.assertRaises(ValueError):
            evaluate(calibration, evaluation, [8000])
