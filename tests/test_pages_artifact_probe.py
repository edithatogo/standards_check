"""Exercise the committed Pages visibility guard without network access or sleeps."""

from contextlib import redirect_stdout
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
        jobs = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]
        cls.build, cls.deploy = jobs["build"], jobs["deploy"]
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

    def execute_probe(self, *responses, environment_overrides=None):
        environment = {
            "PAGES_ARTIFACT_ID": "101", "PAGES_ARTIFACT_NAME": "github-pages-3",
            "GITHUB_RUN_ID": "202", "GITHUB_API_URL": "https://api.github.com",
            "GITHUB_REPOSITORY": "example/repository", "GITHUB_TOKEN": "synthetic-test-token",
        }
        environment.update(environment_overrides or {})
        self.elapsed, self.requests = 0.0, []

        def request(request, *, timeout):
            self.requests.append((request, timeout))
            self.assertLessEqual(len(self.requests), 31, "Probe exceeded the mocked request budget")
            self.assertEqual(request.full_url,
                             "https://api.github.com/repos/example/repository/actions/runs/202/"
                             f"artifacts?name={environment['PAGES_ARTIFACT_NAME']}&per_page=100")
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

    def test_native_upload_precedes_deployment_job_with_producer_identity(self):
        steps = self.deploy["steps"]
        upload = next(step for step in self.build["steps"] if step.get("id") == "pages_upload")
        deploy = next(step for step in steps if step.get("id") == "deployment")
        probe = next(step for step in steps if step.get("name") == self.probe_step["name"])
        self.assertEqual(self.build["env"]["PAGES_ARTIFACT_NAME"],
                         "github-pages-${{ github.run_attempt }}")
        self.assertEqual(upload["with"]["name"], "${{ env.PAGES_ARTIFACT_NAME }}")
        self.assertEqual(self.build["outputs"]["pages_artifact_name"], "${{ env.PAGES_ARTIFACT_NAME }}")
        self.assertEqual(self.build["outputs"]["pages_artifact_id"],
                         "${{ steps.pages_upload.outputs.artifact_id }}")
        self.assertEqual(self.deploy["env"]["PAGES_ARTIFACT_NAME"],
                         "${{ needs.build.outputs.pages_artifact_name }}")
        self.assertEqual(self.deploy["needs"], "build")
        self.assertEqual(upload["if"], self.deploy["if"])
        self.assertFalse(any(step.get("id") == "pages_upload" for step in steps))
        self.assertFalse(any("actions/download-artifact@" in step.get("uses", "") for step in steps))
        self.assertEqual(deploy["with"]["artifact_name"], "${{ env.PAGES_ARTIFACT_NAME }}")
        self.assertEqual(probe["env"]["PAGES_ARTIFACT_ID"],
                         "${{ needs.build.outputs.pages_artifact_id }}")
        self.assertEqual(probe["env"]["GITHUB_TOKEN"], "${{ github.token }}")
        self.assertEqual(self.deploy["permissions"]["actions"], "read")
        self.assertEqual(self.deploy["permissions"]["pages"], "write")
        self.assertEqual(self.deploy["permissions"]["id-token"], "write")
        self.assertEqual(self.deploy["environment"]["name"], "github-pages")
        self.assertLess(steps.index(probe), steps.index(deploy))

    def test_failed_deployment_rerun_keeps_the_successful_build_attempt(self):
        def expand(value, context):
            for key, replacement in context.items():
                value = value.replace("${{ " + key + " }}", str(replacement))
            self.assertNotIn("${{", value, "Unexpected workflow expression in this regression")
            return value

        producer = {"github.run_attempt": 3, "steps.pages_upload.outputs.artifact_id": 101}
        producer["env.PAGES_ARTIFACT_NAME"] = expand(self.build["env"]["PAGES_ARTIFACT_NAME"], producer)
        # GitHub retains successful dependency outputs when only the failed deploy job reruns.
        consumer = {"github.run_attempt": 4}
        consumer.update({"needs.build.outputs." + key: expand(value, producer)
                         for key, value in self.build["outputs"].items()})
        name = expand(self.deploy["env"]["PAGES_ARTIFACT_NAME"], consumer)
        artifact_id = expand(self.probe_step["env"]["PAGES_ARTIFACT_ID"], consumer)
        self.assertEqual((name, artifact_id), ("github-pages-3", "101"))
        output = self.execute_probe(self.payload(self.artifact()), environment_overrides={
            "PAGES_ARTIFACT_NAME": name, "PAGES_ARTIFACT_ID": artifact_id, "GITHUB_RUN_ATTEMPT": "4"})
        self.assertIn("Pages artifact 101 (github-pages-3) is visible for run 202", output)
        self.assertEqual((len(self.requests), self.elapsed), (1, 0))


if __name__ == "__main__":
    unittest.main()
