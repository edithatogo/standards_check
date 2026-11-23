"""Exercise the committed Pages visibility guard without network access or sleeps."""

from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import yaml


class PagesArtifactProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/build-docs.yml"
        cls.deploy = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]["deploy"]
        probes = [step for step in cls.deploy["steps"]
                  if step.get("name") == "Wait for the uploaded Pages artifact metadata"]
        if len(probes) != 1:
            raise AssertionError("Expected exactly one committed Pages artifact probe")
        cls.probe_step = probes[0]
        lines = cls.probe_step["run"].splitlines()
        if lines[0] != "python3 - <<'PY'" or lines[-1] != "PY":
            raise AssertionError("Unexpected Pages probe heredoc; review its test extraction")
        cls.probe = compile("\n".join(lines[1:-1]), "<pages-artifact-probe>", "exec")

    def artifact(self, **changes):
        return {"id": 101, "name": "github-pages-3", "expired": False,
                "workflow_run": {"id": 202}, **changes}

    def payload(self, *artifacts):
        return {"total_count": len(artifacts), "artifacts": list(artifacts)}

    def execute_probe(self, *responses):
        environment = {
            "PAGES_ARTIFACT_ID": "101", "PAGES_ARTIFACT_NAME": "github-pages-3",
            "GITHUB_RUN_ID": "202", "GITHUB_API_URL": "https://api.github.com",
            "GITHUB_REPOSITORY": "example/repository", "GITHUB_TOKEN": "synthetic-test-token",
        }
        self.elapsed, self.requests = 0.0, []

        def request(request, *, timeout):
            self.requests.append((request, timeout))
            self.assertLessEqual(len(self.requests), 31, "Probe exceeded the mocked request budget")
            self.assertEqual(request.full_url,
                             "https://api.github.com/repos/example/repository/actions/runs/202/"
                             "artifacts?name=github-pages-3&per_page=100")
            self.assertEqual(request.get_header("Authorization"), "Bearer synthetic-test-token")
            self.assertGreater(timeout, 0)
            self.assertLessEqual(timeout, min(10, 60 - self.elapsed))
            result = responses[min(len(self.requests) - 1, len(responses) - 1)]
            if isinstance(result, Exception):
                raise result
            return io.StringIO(json.dumps(result))

        def sleep(seconds):
            self.assertGreaterEqual(seconds, 0)
            self.assertLessEqual(seconds, 2)
            self.elapsed += seconds

        output = io.StringIO()
        with patch.dict(os.environ, environment, clear=True), \
             patch("urllib.request.urlopen", side_effect=request), \
             patch("time.monotonic", side_effect=lambda: self.elapsed), \
             patch("time.sleep", side_effect=sleep), redirect_stdout(output):
            exec(self.probe, {"__name__": "__main__"})
        return output.getvalue()

    def test_ready_current_upload_passes_without_waiting(self):
        output = self.execute_probe(self.payload(self.artifact()))
        self.assertIn("Pages artifact 101 (github-pages-3) is visible for run 202", output)
        self.assertEqual((len(self.requests), self.elapsed), (1, 0))

    def test_missing_metadata_is_polled_until_current_upload_is_visible(self):
        self.execute_probe(self.payload(), self.payload(self.artifact()))
        self.assertEqual((len(self.requests), self.elapsed), (2, 2))

    def test_old_attempt_names_do_not_select_the_wrong_upload(self):
        old = self.artifact(id=99, name="github-pages-2")
        self.execute_probe(self.payload(old), self.payload(old, self.artifact()))
        self.assertEqual((len(self.requests), self.elapsed), (2, 2))

    def test_absent_current_upload_times_out_with_bounded_requests(self):
        with self.assertRaisesRegex(SystemExit, "Timed out waiting for Pages artifact 101"):
            self.execute_probe(self.payload())
        self.assertEqual((len(self.requests), self.elapsed), (30, 60))

    def test_duplicate_current_attempt_names_fail(self):
        with self.assertRaisesRegex(SystemExit, "Multiple artifacts match"):
            self.execute_probe(self.payload(self.artifact(), self.artifact(id=102)))
        self.assertEqual((len(self.requests), self.elapsed), (1, 0))

    def test_wrong_upload_id_fails(self):
        with self.assertRaisesRegex(SystemExit, "ID, run or expiry"):
            self.execute_probe(self.payload(self.artifact(id=102)))

    def test_expiry_requires_an_explicit_false_value(self):
        for expired in (True, None, "false"):
            with self.subTest(expired=expired), self.assertRaisesRegex(SystemExit, "ID, run or expiry"):
                self.execute_probe(self.payload(self.artifact(expired=expired)))

    def test_wrong_workflow_run_fails(self):
        with self.assertRaisesRegex(SystemExit, "ID, run or expiry"):
            self.execute_probe(self.payload(self.artifact(workflow_run={"id": 203})))

    def test_incomplete_metadata_fails_even_when_the_expected_upload_is_present(self):
        payload = self.payload(self.artifact())
        payload["total_count"] = 2
        with self.assertRaisesRegex(SystemExit, "metadata is incomplete"):
            self.execute_probe(payload)

    def test_permission_error_is_not_retried_or_reported_as_visibility_success(self):
        error = HTTPError("https://api.github.com", 403, "Forbidden", None, None)
        with self.assertRaises(HTTPError) as observed:
            self.execute_probe(error)
        self.assertEqual(observed.exception.code, 403)
        self.assertEqual((len(self.requests), self.elapsed), (1, 0))

    def test_native_upload_probe_and_deploy_share_the_current_attempt_identity(self):
        steps = deepcopy(self.deploy["steps"])
        upload = next(step for step in steps if step.get("id") == "pages_upload")
        deploy = next(step for step in steps if step.get("id") == "deployment")
        probe = next(step for step in steps if step.get("name") == self.probe_step["name"])
        self.assertEqual(self.deploy["env"]["PAGES_ARTIFACT_NAME"],
                         "github-pages-${{ github.run_attempt }}")
        self.assertEqual(upload["with"]["name"], "${{ env.PAGES_ARTIFACT_NAME }}")
        self.assertEqual(deploy["with"]["artifact_name"], "${{ env.PAGES_ARTIFACT_NAME }}")
        self.assertEqual(probe["env"]["PAGES_ARTIFACT_ID"],
                         "${{ steps.pages_upload.outputs.artifact_id }}")
        self.assertEqual(probe["env"]["GITHUB_TOKEN"], "${{ github.token }}")
        self.assertEqual(self.deploy["permissions"]["actions"], "read")
        self.assertLess(steps.index(upload), steps.index(probe))
        self.assertLess(steps.index(probe), steps.index(deploy))


if __name__ == "__main__":
    unittest.main()
