"""A complete ownership crosswalk must survive adversarial local and API inputs."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate_conductor_links as links


class ConductorLinksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = self.root / "conductor/tracks/00-fixture/plan.md"
        self.plan.parent.mkdir(parents=True)
        self.plan.write_text(
            f"# Fixture\n\n- [ ] **T00.001** ({links.issue_link(1)}) Retain open work.\n"
            f"- [x] **T00.002** ({links.issue_link(2)}) Record the bot dashboard.\n"
        )
        (self.root / "conductor/tracks.md").write_text("| 00 | Fixture |\n")
        self.registry = {
            "schema_version": "dev.standardflow.conductor-issues.v1",
            "repository": links.REPOSITORY,
            "tracks": [{"id": "00", "plan": str(self.plan.relative_to(self.root))}],
            "issues": [
                {"number": 1, "tracks": ["00"], "role": "work", "reverse_link": {"kind": "body"}},
                {"number": 2, "tracks": ["00"], "role": "bot", "reverse_link": {"kind": "comment", "comment_id": 20}},
            ],
        }
        (self.root / links.REGISTRY).parent.mkdir(parents=True)
        self.save()
        self.issues = [
            {"number": n, "html_url": f"https://github.com/{links.REPOSITORY}/issues/{n}",
             "state": "open", "body": links.marker(["00"]) if n == 1 else "Bot owned"}
            for n in (1, 2)
        ]
        self.comments = {2: [{"id": 20, "body": links.marker(["00"])}]}

    def save(self):
        (self.root / links.REGISTRY).write_text(json.dumps(self.registry))

    def check(self):
        return links.validate(self.root, github_issues=self.issues, github_comments=self.comments)

    def test_offline_report_does_not_claim_live_reconciliation(self):
        result = links.validate(self.root)
        self.assertEqual((result["tracks"], result["plan_items"], result["issues"]), (1, 2, 2))
        self.assertEqual(result["plan_item_mapping_percent"], 100)
        self.assertFalse(result["live_github_checked"])
        self.assertFalse(result["reverse_links_checked"])

    def test_live_reconciles_all_issues_ignores_prs_and_retains_completed_history(self):
        self.issues.append({"pull_request": {"url": "ignored"}})
        self.issues[1]["state"] = "closed"
        self.assertTrue(self.check()["live_github_checked"])
        with patch.object(links, "github_pages", side_effect=[self.issues, self.comments[2]]) as fetch:
            self.assertTrue(links.validate(self.root, live=True)["reverse_links_checked"])
        self.assertEqual(fetch.call_count, 2)
        with self.assertRaisesRegex(ValueError, "cannot be mixed"):
            links.validate(self.root, live=True, github_issues=self.issues)

    def test_duplicate_json_keys_and_unknown_fields_are_rejected(self):
        (self.root / links.REGISTRY).write_text('{"repository": "one", "repository": "two"}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            links.validate(self.root)
        self.registry["approval"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "unknown registry fields"):
            links.validate(self.root)

    def test_registry_identity_track_and_issue_constraints(self):
        original = copy.deepcopy(self.registry)
        mutations = [
            lambda r: r.update(schema_version="future"),
            lambda r: r.update(repository="other/repo"),
            lambda r: r.update(tracks=[]),
            lambda r: r["tracks"][0].update(id="0"),
            lambda r: r["tracks"].append(copy.deepcopy(r["tracks"][0])),
            lambda r: r["tracks"][0].update(plan="../outside.md"),
            lambda r: r["tracks"][0].update(unknown=True),
            lambda r: r.update(issues=[]),
            lambda r: r["issues"].append(copy.deepcopy(r["issues"][0])),
            lambda r: r["issues"][0].update(number=True),
            lambda r: r["issues"][0].update(tracks=["00", "00"]),
            lambda r: r["issues"][0].update(tracks=["01"]),
            lambda r: r["issues"][0].update(role=[]),
            lambda r: r["issues"][0].update(reverse_link={"kind": "comment"}),
            lambda r: r["issues"][1].update(reverse_link={"kind": "body"}),
            lambda r: r["issues"][1]["reverse_link"].update(comment_id=False),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.registry = copy.deepcopy(original)
                mutation(self.registry)
                self.save()
                with self.assertRaises(ValueError):
                    links.validate(self.root)

    def test_missing_extra_and_symlinked_plans_are_rejected(self):
        saved = self.plan.read_text()
        self.plan.unlink()
        with self.assertRaises(OSError):
            links.validate(self.root)
        outside = self.root / "outside.md"
        outside.write_text(saved)
        self.plan.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            links.validate(self.root)
        self.plan.unlink()
        self.plan.write_text(saved)
        extra = self.root / "conductor/tracks/01-extra/plan.md"
        extra.parent.mkdir()
        extra.write_text("# Unregistered\n")
        with self.assertRaisesRegex(ValueError, "unregistered"):
            links.validate(self.root)
        extra.unlink()
        (self.root / "conductor/tracks.md").write_text("| 00 | Duplicate |\n| 00 | Duplicate |\n")
        with self.assertRaisesRegex(ValueError, "track table"):
            links.validate(self.root)

    def test_unowned_wrong_track_duplicate_and_forged_task_links_fail(self):
        original = self.plan.read_text()
        variants = [
            original + "- [ ] Unowned work\n",
            original + "+ [ ] Unowned work\n",
            original + "1. [ ] Unowned work\n",
            original + "2) [ ] Unowned work\n",
            original + "-  [ ] Unowned work\n",
            original + "*\t[ ] Unowned work\n",
            original + "- [\t] Unowned work\n",
            original + "> - [ ] Unowned work\n",
            original.replace("- [ ]", "    - [ ]"),
            original.replace("T00.001", "T01.001"),
            original.replace("T00.002", "T00.001"),
            original.replace(links.issue_link(1), links.issue_link(3)),
            original.replace(links.issue_link(1), links.issue_link(1) + ", " + links.issue_link(1)),
            original.replace("standards_check/issues/1", "another_repo/issues/1"),
            original.replace(links.issue_link(1), ""),
            "# No checkbox tasks\n",
            original.splitlines()[0] + "\n" + original.splitlines()[2] + "\n",
        ]
        for variant in variants:
            with self.subTest(variant=variant):
                self.plan.write_text(variant)
                with self.assertRaises(ValueError):
                    links.validate(self.root)

    def test_fenced_and_commented_examples_cannot_establish_ownership(self):
        original = self.plan.read_text()
        for start, end in [("```markdown", "```"), ("~~~~", "~~~~~"), ("<!--", "-->")]:
            with self.subTest(start=start):
                self.plan.write_text(start + "\n" + original + "\n" + end + "\n")
                with self.assertRaisesRegex(ValueError, "no registered plan items"):
                    links.validate(self.root)
                self.plan.write_text(original + "\n" + start + "\n- [ ] Example only\n" + end + "\n")
                self.assertEqual(links.validate(self.root)["plan_items"], 2)
        self.plan.write_text(original + "\n<!-- One-line comment -->\n<!-- Two\nlines -->\n")
        self.assertEqual(links.validate(self.root)["plan_items"], 2)
        for suffix in ("\n```markdown\n- [ ] Hidden\n", "\n<!--\n- [ ] Hidden\n"):
            self.plan.write_text(original + suffix)
            with self.assertRaisesRegex(ValueError, "unclosed plan"):
                links.validate(self.root)

    def test_declared_track_must_actually_own_a_task(self):
        second = self.root / "conductor/tracks/01-fixture/plan.md"
        second.parent.mkdir()
        second.write_text(f"- [x] **T01.001** ({links.issue_link(2)}) Track one work.\n")
        self.registry["tracks"].append({"id": "01", "plan": str(second.relative_to(self.root))})
        for issue in self.registry["issues"]:
            issue["tracks"].append("01")
        self.save()
        (self.root / "conductor/tracks.md").write_text("| 00 | First |\n| 01 | Second |\n")
        with self.assertRaisesRegex(ValueError, "lack corresponding"):
            links.validate(self.root)

    def test_live_identity_and_exact_universe_are_mandatory(self):
        original = copy.deepcopy(self.issues)
        for variant in [[], original[:1], original + [original[0]],
                        [None], [{**original[0], "number": True}, original[1]],
                        [{**original[0], "html_url": "https://github.com/other/repo/issues/1"}, original[1]],
                        [{**original[0], "state": "draft"}, original[1]],
                        original + [{"number": 3, "html_url": f"https://github.com/{links.REPOSITORY}/issues/3", "state": "open"}]]:
            with self.subTest(variant=variant):
                self.issues = variant
                with self.assertRaises(ValueError):
                    self.check()

    def test_missing_and_ambiguous_reverse_links_fail(self):
        for body in (None, "", links.marker(["01"]), links.marker(["00"]) * 2):
            with self.subTest(body=body):
                self.issues[0]["body"] = body
                with self.assertRaisesRegex(ValueError, "issue reverse link"):
                    self.check()
        self.issues[0]["body"] = links.marker(["00"])
        for comments in ({}, {2: []}, {2: [{"id": 21, "body": links.marker(["00"])}]},
                         {2: [{"id": 20, "body": "missing"}]},
                         {2: self.comments[2] * 2}):
            with self.subTest(comments=comments):
                with self.assertRaisesRegex(ValueError, "bot reverse link"):
                    links.validate(self.root, github_issues=self.issues, github_comments=comments)

    def test_closed_owner_cannot_hide_unfinished_work(self):
        self.issues[0]["state"] = "closed"
        with self.assertRaisesRegex(ValueError, "unfinished task"):
            self.check()
        self.plan.write_text(self.plan.read_text().replace("[ ]", "[x]"))
        self.assertTrue(self.check()["live_github_checked"])

    def test_github_reader_is_paginated_and_fails_closed(self):
        endpoint = "repos/example/repo/issues?state=all"
        result = subprocess.CompletedProcess([], 0, json.dumps([self.issues, []]), "")
        with patch.object(links.subprocess, "run", return_value=result) as run:
            self.assertEqual(links.github_pages(endpoint), self.issues)
        self.assertEqual(run.call_args.args[0], ["gh", "api", "--paginate", "--slurp", endpoint])
        self.assertFalse(run.call_args.kwargs.get("shell", False))
        result.returncode = 1
        result.stderr = "sensitive diagnostic must not be repeated"
        with patch.object(links.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "read failed"):
                links.github_pages(endpoint)
        self.assertEqual(links.flatten_pages(self.issues), self.issues)
        for invalid in ({}, [1], [self.issues, {}]):
            with self.assertRaises(ValueError):
                links.flatten_pages(invalid)

    def test_cli_reports_success_and_returns_nonzero_for_invalid_registry(self):
        with patch.object(sys, "argv", ["validate", "--root", str(self.root)]), patch("builtins.print") as output:
            self.assertEqual(links.main(), 0)
            self.assertFalse(json.loads(output.call_args.args[0])["live_github_checked"])
        self.registry["repository"] = "wrong/repository"
        self.save()
        with patch.object(sys, "argv", ["validate", "--root", str(self.root)]), patch("builtins.print") as output:
            self.assertEqual(links.main(), 1)
            self.assertIn("ERROR", output.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
