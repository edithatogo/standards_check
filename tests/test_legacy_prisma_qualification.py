"""Bounded migration evidence must reject invented or inconsistent source facts."""

from copy import deepcopy
import json
import unittest

from scripts import qualify_legacy_prisma as qualification


class TestLegacyPrismaQualification(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(qualification.CORPUS.read_text())["cases"]
        self.case = deepcopy(self.cases[0])
        self.legacy = json.loads(
            (qualification.LEGACY / self.case["legacy_fixture"]).read_text()
        )

    def test_both_authored_pairs_satisfy_the_bounded_contract(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                legacy = json.loads((qualification.LEGACY / case["legacy_fixture"]).read_text())
                qualification.validate_pair(case, legacy)

    def test_missing_or_false_conditions_cannot_be_inferred(self):
        for value in (None, False, "true"):
            with self.subTest(value=value):
                case = deepcopy(self.case)
                case["conditions"]["one_report_per_included_study"] = value
                with self.assertRaisesRegex(ValueError, "explicit conditions"):
                    qualification.validate_pair(case, self.legacy)

    def test_missing_count_is_not_filled_with_zero(self):
        del self.case["rust_input"]["databases_registers"]["registers"]
        with self.assertRaisesRegex(ValueError, "explicit database counts"):
            qualification.validate_pair(self.case, self.legacy)

    def test_multiple_reports_per_study_are_outside_this_contract(self):
        self.case["rust_input"]["new_included"]["reports"] += 1
        with self.assertRaisesRegex(ValueError, "one report per included study"):
            qualification.validate_pair(self.case, self.legacy)

    def test_legacy_counts_must_match_the_authored_expectations(self):
        self.legacy["records_screened"] += 1
        with self.assertRaisesRegex(ValueError, "legacy counts"):
            qualification.validate_pair(self.case, self.legacy)

    def test_matching_bad_inputs_do_not_establish_arithmetic_parity(self):
        self.case["expected_counts"]["records_excluded"] += 1
        self.case["rust_input"]["databases_registers"]["records_excluded"] += 1
        self.legacy["records_excluded"] += 1
        with self.assertRaisesRegex(ValueError, "count conservation"):
            qualification.validate_pair(self.case, self.legacy)

    def test_updated_review_requires_disjoint_previous_and_new_studies(self):
        case = deepcopy(self.cases[1])
        del case["conditions"]["previous_and_new_studies_disjoint"]
        legacy = json.loads((qualification.LEGACY / case["legacy_fixture"]).read_text())
        with self.assertRaisesRegex(ValueError, "explicit conditions"):
            qualification.validate_pair(case, legacy)


if __name__ == "__main__":
    unittest.main()
