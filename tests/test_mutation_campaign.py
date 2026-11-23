"""Mutation evidence must never count infrastructure failures as assertion kills."""

import unittest

from tests.mutation_campaign import classify


class MutationOutcomeTests(unittest.TestCase):
    def test_assertion_only_failures_are_kills(self):
        for group, output in (
            ("python", "FAIL: fixture\nAssertionError\nFAILED (failures=1)\n"),
            ("api", "  code: 'ERR_ASSERTION'\n# fail 1\n"),
        ):
            with self.subTest(group=group):
                self.assertEqual(classify({"exit_code": 1, "timed_out": False,
                                           "output": output}, group), "assertion_kill")

    def test_survivors_timeouts_and_mixed_failures_remain_distinct(self):
        for group, code, timed_out, output, expected in (
            ("python", 0, False, "OK", "survived"),
            ("api", None, True, "", "timeout"),
            ("python", 1, False, "ImportError: unavailable dependency", "unviable"),
            ("python", 1, False, "AssertionError\nERROR: setup\nFAILED (failures=1, errors=1)", "unviable"),
            ("api", 1, False, "  code: 'ERR_ASSERTION'\n# fail 2\n", "unviable"),
            ("api", 1, False, "failureType: 'hookFailed'\n  code: 'ERR_ASSERTION'\n# fail 1\n", "unviable"),
            ("api", -9, False, "  code: 'ERR_ASSERTION'\n# fail 1\n", "unviable"),
        ):
            with self.subTest(group=group, expected=expected, output=output):
                self.assertEqual(classify({"exit_code": code, "timed_out": timed_out,
                                           "output": output}, group), expected)
