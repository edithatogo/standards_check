"""Regression checks for generated HTML accessibility contracts."""

import unittest

from scripts.verify_site_accessibility import problems


VALID = (
    '<!DOCTYPE html><html lang="en"><body>'
    '<a href="#main-content">Skip to main content</a>'
    '<h1>Checklist</h1><main id="main-content" tabindex="-1">'
    '<div role="progressbar" aria-label="Checklist completion">0%</div>'
    '</main></body></html>'
)


class SiteAccessibilityContractTests(unittest.TestCase):
    def test_valid_page(self) -> None:
        self.assertEqual(problems(VALID), [])

    def test_extra_h1_is_rejected(self) -> None:
        self.assertIn("exactly one h1", " ".join(problems(VALID.replace("</main>", "<h1>Duplicate</h1></main>"))))

    def test_missing_skip_link_or_main_target_is_rejected(self) -> None:
        self.assertTrue(problems(VALID.replace('href="#main-content"', 'href="#missing"')))
        self.assertTrue(problems(VALID.replace('id="main-content"', 'id="missing"')))

    def test_unnamed_progress_is_rejected(self) -> None:
        self.assertIn("progress bars", " ".join(problems(VALID.replace(' aria-label="Checklist completion"', ""))))


if __name__ == "__main__":
    unittest.main()
