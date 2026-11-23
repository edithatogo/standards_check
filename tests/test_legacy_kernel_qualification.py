"""Prevent false acceptance of incomplete or unequal real-kernel receipts."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from scripts import qualify_legacy_kernel as kernel


def receipts():
    notebooks = []
    for path in sorted((kernel.ROOT / "legacy/standardflow/examples/notebooks").glob("*.ipynb")):
        cells = json.loads(path.read_text())["cells"]
        notebooks.append({"name": path.name,
                          "code_cells": sum(c["cell_type"] == "code" for c in cells),
                          "visible_output_sha256": "fixture-output",
                          "shutdown_reply_observed": True})
    first = {
        "result": "pass", "ipykernel": "6.25.0", "python": "3.12",
        "dependencies": {f"package-{i}": "1" for i in range(41)} | {"ipykernel": "6.25.0"},
        "notebooks": notebooks, "clean_shutdowns": 11, "saved_notebook_outputs_used": False,
        "rendered_images": {f"diagram-{i}.png": "fixture-png" for i in range(6)},
        "application": {"tests": 52, "files": {f"file-{i}": {} for i in range(21)}},
        "provenance": {"source_tree": "fixture-tree"},
        "host_profile_sha256": "fixture-host", "kernel_profile_sha256": "fixture-kernel",
        "protocol": dict.fromkeys(kernel.PROTOCOL_CHECKS, True),
    }
    second = deepcopy(first)
    second["ipykernel"] = second["dependencies"]["ipykernel"] = "6.31.0"
    return first, second


class LegacyKernelQualificationTests(unittest.TestCase):
    def test_equal_complete_receipts_accept_only_the_kernel_version_difference(self):
        self.assertEqual(kernel.compare(*receipts())["identical_cli_files"], 21)

    def test_failed_or_wrong_version_receipt_is_not_a_pass(self):
        for key, value in (("result", "fail"), ("ipykernel", "6.25.0")):
            with self.subTest(key=key):
                baseline, candidate = receipts()
                candidate[key] = value
                with self.assertRaisesRegex(ValueError, "successful, correctly identified"):
                    kernel.compare(baseline, candidate)

    def test_changed_other_dependency_is_rejected(self):
        baseline, candidate = receipts()
        candidate["dependencies"]["package-0"] = "2"
        with self.assertRaisesRegex(ValueError, "differ beyond"):
            kernel.compare(baseline, candidate)

    def test_installed_kernel_identity_must_match_the_claimed_version(self):
        baseline, candidate = receipts()
        for receipt in (baseline, candidate):
            receipt["dependencies"]["ipykernel"] = "0.0.0"
        with self.assertRaisesRegex(ValueError, "installed kernel version"):
            kernel.compare(baseline, candidate)

    def test_changed_notebook_output_or_rendered_image_is_rejected(self):
        for field in ("notebooks", "rendered_images"):
            with self.subTest(field=field):
                baseline, candidate = receipts()
                if field == "notebooks":
                    candidate[field][0]["visible_output_sha256"] = "different"
                else:
                    candidate[field]["diagram-0.png"] = "different"
                with self.assertRaisesRegex(ValueError, f"differs: {field}"):
                    kernel.compare(baseline, candidate)

    def test_equal_but_incomplete_evidence_is_rejected(self):
        for mutation in (
            lambda r: r["notebooks"].pop(),
            lambda r: r["notebooks"][0].update(code_cells=0),
            lambda r: r["notebooks"][0].update(shutdown_reply_observed=False),
            lambda r: r.update(clean_shutdowns=10),
            lambda r: r.update(saved_notebook_outputs_used=True),
            lambda r: r["protocol"].update(interrupt_and_recovery=False),
            lambda r: r["application"].update(tests=0),
            lambda r: r["application"].update(files={}),
        ):
            baseline, candidate = receipts()
            mutation(baseline)
            mutation(candidate)
            with self.assertRaisesRegex(ValueError, "incomplete|lacks complete"):
                kernel.compare(baseline, candidate)

    def test_shutdown_reply_is_insufficient_without_successful_process_exit(self):
        for outcome in (1, subprocess.TimeoutExpired("kernel", 15)):
            with self.subTest(outcome=outcome):
                manager, client = Mock(), Mock()
                client.shutdown.return_value = {"content": {"restart": False}}
                if isinstance(outcome, Exception):
                    manager.provisioner.process.wait.side_effect = outcome
                else:
                    manager.provisioner.process.wait.return_value = outcome
                with self.assertRaises((RuntimeError, subprocess.TimeoutExpired)):
                    kernel.shutdown(manager, client)

    def test_shutdown_requires_acknowledgement_and_successful_exit(self):
        manager, client = Mock(), Mock()
        client.shutdown.return_value = {"content": {"restart": False}}
        manager.provisioner.process.wait.return_value = 0
        kernel.shutdown(manager, client)
        manager.provisioner.process.wait.assert_called_once_with(timeout=15)
        client.shutdown.return_value = {"content": {"restart": True}}
        with self.assertRaisesRegex(RuntimeError, "acknowledge"):
            kernel.shutdown(manager, client)

    def test_kernel_error_cannot_be_silently_accepted(self):
        client = Mock()
        client.execute_interactive.return_value = {"content": {"status": "error", "ename": "ValueError"}}
        with self.assertRaisesRegex(RuntimeError, "Unexpected kernel execution"):
            kernel.execute(client, "bad input")

    def test_iopub_error_overrides_an_inconsistent_ok_reply(self):
        client = Mock()

        def wrong_reply(code, **kwargs):
            kwargs["output_hook"]({"msg_type": "error", "content": {"ename": "ValueError"}})
            return {"content": {"status": "ok"}}

        client.execute_interactive.side_effect = wrong_reply
        with self.assertRaisesRegex(RuntimeError, "emitted an error"):
            kernel.execute(client, "bad input")

    def test_stream_chunks_coalesce_without_losing_stderr_or_display_content(self):
        messages = [{"msg_type": "stream", "content": {"name": "stdout", "text": text}}
                    for text in ("a", "b")]
        messages += [{"msg_type": "stream", "content": {"name": "stderr", "text": "warning"}},
                     {"msg_type": "display_data", "content": {
                         "data": {"text/markdown": "# Title"}, "metadata": {"needs_background": "light"}}}]
        visible = kernel.outputs(messages)
        self.assertEqual([item.get("text") for item in visible], ["ab", "warning", None])
        self.assertEqual(visible[-1]["data"], {"text/markdown": "# Title"})
        self.assertEqual(visible[-1]["metadata"], {"needs_background": "light"})

    def test_failed_execution_writes_failure_and_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            with patch("sys.argv", ["qualify", "--expected-version", "6.31.0", "--output", str(output)]):
                with patch.object(kernel, "qualify", side_effect=RuntimeError("startup failed")):
                    with patch("builtins.print"):
                        self.assertEqual(kernel.main(), 1)
            self.assertEqual(json.loads(output.read_text())["result"], "fail")


if __name__ == "__main__":
    unittest.main()
