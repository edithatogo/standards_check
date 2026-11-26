import unittest

from scripts.layout_development import facts, score


class LayoutDevelopmentTests(unittest.TestCase):
    def test_exact_qualifier_link_requires_correct_owner(self):
        gold = [("qualifier_link", 1, "1.1", "a")]
        predicted = facts(["1.2  Report harm. [a]\n[a] Except when withheld."])
        result = score(gold, predicted)
        self.assertEqual(result["qualifier_link"]["tp"], 0)
        self.assertEqual(result["qualifier_link"]["fn"], 1)
        self.assertEqual(result["qualifier_link"]["fp"], 1)

    def test_nested_requires_parent_and_exact_rows_include_continuation(self):
        result = facts(["1.1  Report outcomes.\n     Include missing data.\n1.1.1  If measured, report timing."])
        self.assertIn(("row", 1, "1.1", "Report outcomes. Include missing data."), [x[0] for x in result])
        self.assertIn(("nested", 1, "1.1.1", "1.1"), [x[0] for x in result])
        orphan = facts(["1.1.1  If measured, report timing."])
        self.assertFalse(any(x[0][0] == "nested" for x in orphan))

    def test_duplicate_predictions_penalised_and_page_mismatch_fails(self):
        gold = [("row", 1, "1.1", "Report outcomes.")]
        duplicate = facts(["1.1 Report outcomes.\n1.1 Report outcomes."])
        self.assertEqual(score(gold, duplicate)["row"]["fp"], 1)
        self.assertEqual(score(gold, facts(["", "1.1 Report outcomes."]))["row"]["tp"], 0)

    def test_score_column_requires_explicit_layout_separator(self):
        result = facts(["Sub-item number   Sub-item   Score\n1.1  Report outcomes.   8.3"])
        self.assertIn(("row", 1, "1.1", "Report outcomes."), [x[0] for x in result])
        ambiguous = facts(["Sub-item number Sub-item Score\n1.1 Report outcomes. 8.3"])
        self.assertIn(("row", 1, "1.1", "Report outcomes. 8.3"), [x[0] for x in ambiguous])

    def test_reference_region_not_used_to_generate_predictions(self):
        result = facts(["1.1 Report outcomes. [a]\n[a] Except when withheld."])
        self.assertTrue(all(anchor.startswith("page/1/lines/") for _, anchor in result))
        self.assertIn(("footnote", 1, "a", "Except when withheld."), [x[0] for x in result])


if __name__ == "__main__":
    unittest.main()
