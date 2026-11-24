"""Synthetic structural regression controls; legacy items are not authority."""
import unittest

from scripts.legacy_checklist_structure import parse_legacy_tasks


class LegacyStructureTests(unittest.TestCase):
    def test_nested_bullets_and_wrapped_lines_preserved_with_anchors(self):
        rows = parse_legacy_tasks(
            "## Abstract\n- [ ] **2. Summary:** Report the following:\n"
            "    - Methods and outcomes.\n      Include adverse events.\n"
            "\n    - Registration information.\n## Methods\n- [x] **3a.** Report setting.\n"
            "## Notes\n- Reviewer instructions.\n")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["text"], "Report the following:\n- Methods and outcomes.\nInclude adverse events.\n- Registration information.")
        self.assertEqual(rows[0]["line_numbers"], [2, 3, 4, 6])
        self.assertEqual(rows[0]["line_indents"], [0, 4, 6, 4])
        self.assertTrue(rows[0]["raw_text"].startswith("**2. Summary:**"))
        self.assertEqual(rows[0]["declared_item_id"], "2")
        self.assertEqual(rows[0]["section_line"], 1)
        self.assertEqual(rows[1]["declared_item_id"], "3a")
        self.assertEqual(rows[1]["line_numbers"], [8])
        self.assertEqual(rows[1]["section_line"], 7)

    def test_nested_tasks_retain_parent_and_do_not_duplicate_child_text(self):
        rows = parse_legacy_tasks(
            "- [ ] **S1. Topic:** Parent.\n    - [ ] **1.1** Child.\n"
            "        Child continuation.\n    - [x] **1.2a** Other child.\n"
            "- [ ] **Unnumbered topic:** Sibling.\n")
        self.assertEqual([r["position"] for r in rows], [1, 2, 3, 4])
        self.assertEqual([r["parent_position"] for r in rows], [None, 1, 1, None])
        self.assertEqual([r["declared_item_id"] for r in rows], ["s1", "1.1", "1.2a", None])
        self.assertEqual(rows[0]["text"], "Parent.")
        self.assertEqual(rows[1]["text"], "Child.\nChild continuation.")
        self.assertEqual(rows[3]["text"], "Sibling.")

    def test_outdent_returns_to_parent(self):
        rows = parse_legacy_tasks("- [ ] Parent.\n    - [ ] Child.\n  Parent continuation.\n")
        self.assertEqual(rows[0]["text"], "Parent.\nParent continuation.")
        self.assertEqual(rows[0]["line_numbers"], [1, 3])
        self.assertEqual(rows[1]["text"], "Child.")

    def test_fenced_examples_and_non_task_notes_are_not_items(self):
        rows = parse_legacy_tasks(
            "```md\n- [ ] Example only.\n```\n"
            "- [ ] Real item.\n\n- Notes, not a requirement.\n    Note details.\n"
            "- [ ] Another item.\n")
        self.assertEqual([r["text"] for r in rows], ["Real item.", "Another item."])
        self.assertEqual([r["line_numbers"] for r in rows], [[4], [8]])

    def test_lazy_continuation_is_retained_but_flagged_and_empty_task_visible(self):
        rows = parse_legacy_tasks("- [ ] First line\npossible continuation.\n\n- [ ]\n")
        self.assertEqual(rows[0]["text"], "First line\npossible continuation.")
        self.assertEqual(rows[0]["warnings"], ["ambiguous_unindented_continuation"])
        self.assertEqual(rows[1]["text"], "")
        self.assertEqual(rows[1]["warnings"], ["empty_requirement"])

    def test_task_fence_is_held_and_not_parsed_as_child_task(self):
        rows = parse_legacy_tasks("- [ ] Item.\n    ```\n    - [ ] Example.\n    ```\n- [ ] Other.\n")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["warnings"], ["fenced_content_requires_review"])
        self.assertEqual(rows[0]["line_numbers"], [1, 2, 3, 4])
        self.assertIn("Example.", rows[0]["text"])


if __name__ == "__main__":
    unittest.main()
