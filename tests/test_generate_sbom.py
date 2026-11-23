"""SBOM identity, checkout binding and fail-closed evidence; no network needed."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import generate_sbom as sbom


def bom(*packages, ecosystem="npm"):
    return {"bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1,
            "components": [{"type": "library", "name": name, "version": version,
                            "purl": f"pkg:{ecosystem}/{name}@{version}"} for name, version in packages]}


class SbomTests(unittest.TestCase):
    def test_inventory_requires_every_exact_identity(self):
        expected = {("example-pkg", "1.2")}
        sbom.verify_inventory(bom(("Example_Pkg", "1.2"), ecosystem="pypi"), expected, "pypi")
        for document in (bom(), bom(("example-pkg", "1.3")),
                         bom(("example-pkg", "1.2"), ("unexpected", "2"))):
            with self.subTest(document=document), self.assertRaisesRegex(ValueError, "inventory mismatch"):
                sbom.verify_inventory(document, expected, "npm")
        for extra in ({"name": "foreign", "version": "2", "purl": "pkg:pypi/foreign@2"},
                      {"name": "unidentified", "version": "1"}, None):
            document = bom(("example-pkg", "1.2"))
            document["components"].append(extra)
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "only identifiable npm"):
                sbom.verify_inventory(document, expected, "npm")
        with self.assertRaisesRegex(ValueError, "array"):
            sbom.verify_inventory({"components": {}}, expected, "npm")
        with self.assertRaisesRegex(ValueError, "JSON object"):
            sbom.verify_inventory([], expected, "npm")

    def test_native_npm_inventory_uses_all_locked_identities(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            api = root / "api"
            api.mkdir()
            lock = {"packages": {"": {"name": "app", "version": "1"},
                                 "node_modules/example": {"version": "2", "dev": True},
                                 "node_modules/@scope/optional": {"version": "3", "optional": True}}}
            for base in (root, api):
                (base / "package-lock.json").write_text(json.dumps(lock))
            for component in ("node", "api"):
                for complete in (True, False):
                    document = bom(("example", "2"), *(([("@scope/optional", "3")]) if complete else []))
                    receipt = {}
                    with self.subTest(component=component, complete=complete), patch.object(sbom, "ROOT", root), \
                         patch.object(sbom, "run", side_effect=[json.dumps(document), "v24", "11"]) as command:
                        if complete:
                            sbom.generate(component, root, root, root, receipt)
                            self.assertEqual(receipt["locked_package_records"], 2)
                            self.assertIn("--package-lock-only", command.call_args_list[0].args[0])
                            self.assertIn("--include=optional", command.call_args_list[0].args[0])
                        else:
                            with self.assertRaisesRegex(ValueError, "inventory mismatch"):
                                sbom.generate(component, root, root, root, receipt)

    def test_pinned_central_helper_bytes_are_checked_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = Path(directory)
            (policy / "scripts").mkdir()
            helper = policy / "scripts" / "example.py"
            helper.write_text("value = 42\n")
            with patch.object(sbom.subprocess, "check_output", return_value=helper.read_bytes()):
                self.assertEqual(sbom.central_helper(policy, "example.py").value, 42)
                helper.write_text("raise RuntimeError('untrusted modified helper')\n")
                with self.assertRaisesRegex(ValueError, "pinned policy revision"):
                    sbom.central_helper(policy, "example.py")

    def test_collect_binds_bytes_and_preserves_failure_receipts(self):
        for mode in ("success", "dirty-rejected", "dirty-recorded", "mutated", "tool-error"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "package.json").write_text("{}")
                (root / "package-lock.json").write_text("{}")
                output = root / "evidence"
                def generate(*args):
                    if mode == "mutated":
                        (root / "package-lock.json").write_text('{"changed":true}')
                    if mode == "tool-error":
                        raise subprocess.CalledProcessError(2, ["inventory-tool"], output="partial", stderr="failure")
                    return bom(("example", "1"))
                checker = SimpleNamespace(inventory_summary=lambda document: {"identified_packages": 1})
                with patch.object(sbom, "ROOT", root), patch.object(sbom, "run", return_value="a" * 40), \
                     patch.object(sbom.subprocess, "check_output", return_value=b"different" if mode.startswith("dirty") else b"{}"), \
                     patch.object(sbom, "generate", side_effect=generate), patch.object(sbom, "central_helper", return_value=checker):
                    receipt = sbom.collect("node", output, root, allow_dirty=mode == "dirty-recorded")
                self.assertEqual(json.loads((output / "receipt.json").read_text()), receipt)
                passed = mode in ("success", "dirty-recorded")
                self.assertEqual(receipt["outcome"], "success" if passed else "error")
                self.assertEqual((output / "bom.cdx.json").exists(), passed)
                if passed:
                    self.assertEqual(receipt["bom_sha256"], sbom.digest((output / "bom.cdx.json").read_bytes()))
                    self.assertEqual(bool(receipt["modified_inputs"]), mode == "dirty-recorded")
                else:
                    self.assertIn("error", receipt)
                for line in (output / "SHA256SUMS").read_text().splitlines():
                    checksum, name = line.split("  ")
                    self.assertEqual(checksum, sbom.digest((output / name).read_bytes()))

    def test_python_inventory_rejects_pin_omission_closure_and_tool_drift(self):
        for mode in ("success", "omitted", "extra", "pin-drift", "tool-drift", "range"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "requirements").mkdir()
                (root / "requirements" / "fixture.txt").write_text("example>=1\n" if mode == "range" else "example==1\n")
                installed = [{"metadata": {"name": "example", "version": "2" if mode == "pin-drift" else "1"}}]
                if mode == "extra":
                    installed.append({"metadata": {"name": "unlocked", "version": "1"}})
                document = bom(*([] if mode == "omitted" else [("example", "1")]), ecosystem="pypi")
                def command(args, **kwargs):
                    if "inspect" in args:
                        return json.dumps({"installed": installed})
                    if "version" in args:
                        return json.dumps({"version": "different" if mode == "tool-drift" else "1.57.2"})
                    return json.dumps(document) if "scan" in args else ""
                scanner = SimpleNamespace(download_tool=lambda name, output: (root / "syft", {"version": "1.57.2"}))
                with patch.object(sbom, "ROOT", root), patch.dict(sbom.PYTHON_PROFILES, {"fixture": ("fixture", sys.version_info[:2], True)}), \
                     patch.object(sbom, "run", side_effect=command) as run, patch.object(sbom, "central_helper", return_value=scanner):
                    receipt = {"source_commit": "a" * 40}
                    if mode == "success":
                        sbom.python_inventory("python-fixture", root, root, root, receipt)
                        self.assertEqual(receipt["installed_distributions"], 1)
                        self.assertIn("exact profile closure", receipt["resolution"])
                    else:
                        with self.assertRaises(ValueError):
                            sbom.python_inventory("python-fixture", root, root, root, receipt)
                        if mode == "range":
                            run.assert_not_called()

    def test_cli_rejects_stale_or_symlink_output_and_reports_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stale = root / "stale"
            stale.mkdir()
            (stale / "prior-evidence").write_text("preserve")
            linked = root / "link"
            linked.symlink_to(stale, target_is_directory=True)
            for output in (stale, linked):
                with patch.object(sys, "argv", ["sbom", "--component", "node", "--policy-dir", str(root), "--output", str(output)]), \
                     contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(sbom.main(), 1)
                self.assertEqual((stale / "prior-evidence").read_text(), "preserve")

    def test_python_version_marker_selects_numeric_boundary_and_exact_closure(self):
        cases = [((3, 12), '"', True, True), ((3, 13), '"', False, True),
                 ((3, 14), '"', False, True), ((3, 9), "'", True, True),
                 ((3, 12), '"', False, False), ((3, 14), '"', True, False)]
        for runtime, quote, installed_conditional, should_pass in cases:
            with self.subTest(runtime=runtime, installed_conditional=installed_conditional), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                requirements = root / "requirements/fixture.txt"
                requirements.parent.mkdir()
                declared = f"example==1\ntyping-extensions==4.16.0; python_version < {quote}3.13{quote}\n"
                requirements.write_text(declared)
                packages = [("example", "1"), *([("typing-extensions", "4.16.0")] if installed_conditional else [])]
                def command(args, **kwargs):
                    if "inspect" in args:
                        return json.dumps({"installed": [{"metadata": {"name": name, "version": pin}} for name, pin in packages]})
                    if "version" in args:
                        return json.dumps({"version": "1.57.2"})
                    return json.dumps(bom(*packages, ecosystem="pypi")) if "scan" in args else ""
                scanner = SimpleNamespace(download_tool=lambda name, output: (root / "syft", {"version": "1.57.2"}))
                with patch.object(sbom, "ROOT", root), patch.object(sbom.sys, "version_info", runtime), \
                     patch.dict(sbom.PYTHON_PROFILES, {"fixture": ("fixture", runtime, True)}), \
                     patch.object(sbom, "run", side_effect=command) as run, patch.object(sbom, "central_helper", return_value=scanner):
                    receipt = {"source_commit": "a" * 40}
                    if should_pass:
                        sbom.python_inventory("python-fixture", root, root, root, receipt)
                        self.assertEqual(receipt["installed_distributions"], len(packages))
                        install = next(call.args[0] for call in run.call_args_list if "install" in call.args[0])
                        self.assertIn(str(requirements), install)
                        self.assertIn("--no-deps", install)
                    else:
                        with self.assertRaisesRegex(ValueError, "declared dependency profile"):
                            sbom.python_inventory("python-fixture", root, root, root, receipt)
                self.assertEqual(requirements.read_text(), declared)

    def test_unsupported_python_markers_fail_before_install_even_when_inactive(self):
        declarations = [
            'example==1; python_version <= "3.13"',
            'example==1; python_version < "3.13" and sys_platform == "linux"',
            'example==1; python_version < "3.13',
            "example==1; python_version < '3.13\"",
            'example==1; python_version < "3.13.0"',
            'example==1; python_full_version < "3.13"',
            'example>=1; python_version < "2.0"',
            'example; python_version < "2.0"',
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements = root / "requirements/fixture.txt"
            requirements.parent.mkdir()
            for declaration in declarations:
                requirements.write_text(declaration + "\n")
                with self.subTest(declaration=declaration), patch.object(sbom, "ROOT", root), \
                     patch.dict(sbom.PYTHON_PROFILES, {"fixture": ("fixture", sys.version_info[:2], True)}), \
                     patch.object(sbom, "run") as run, self.assertRaisesRegex(ValueError, "expected exact"):
                    sbom.python_inventory("python-fixture", root, root, root, {})
                run.assert_not_called()

    def test_kernel_inventory_uses_both_profiles_and_workflow_owned_pins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements").mkdir()
            (root / "requirements/legacy-standardflow.txt").write_text("host==1\n")
            (root / "requirements/legacy-kernel-qualification.txt").write_text("extension==2\n")
            workflow = root / ".github/workflows/standardflow-legacy.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("          for kernel_version in 6.25.0 6.31.0; do\n")
            scanner = SimpleNamespace(download_tool=lambda name, output: (root / "syft", {"version": "1.57.2"}))
            for role, version in (("baseline", "6.25.0"), ("candidate", "6.31.0")):
                packages = [("host", "1"), ("extension", "2"), ("ipykernel", version)]
                def command(args, **kwargs):
                    if "inspect" in args:
                        return json.dumps({"installed": [{"metadata": {"name": name, "version": pin}} for name, pin in packages]})
                    if "version" in args:
                        return json.dumps({"version": "1.57.2"})
                    return json.dumps(bom(*packages, ecosystem="pypi")) if "scan" in args else ""
                with self.subTest(role=role), patch.object(sbom, "ROOT", root), \
                     patch.dict(sbom.PYTHON_PROFILES, {f"kernel-{role}": ("legacy-kernel-qualification", sys.version_info[:2], True)}), \
                     patch.object(sbom, "run", side_effect=command) as run, patch.object(sbom, "central_helper", return_value=scanner):
                    receipt = {"source_commit": "a" * 40}
                    sbom.python_inventory(f"python-kernel-{role}", root, root, root, receipt)
                    install = next(call.args[0] for call in run.call_args_list if "install" in call.args[0])
                    self.assertEqual(install.count("-r"), 2)
                    self.assertIn(f"ipykernel=={version}", install)
                    self.assertEqual(receipt["kernel_version"], version)
                    self.assertIn(workflow, sbom.source_inputs(f"python-kernel-{role}"))
            workflow.write_text("for kernel_version in latest; do\n")
            with patch.object(sbom, "ROOT", root), \
                 patch.dict(sbom.PYTHON_PROFILES, {"kernel-baseline": ("legacy-kernel-qualification", sys.version_info[:2], True)}), \
                 patch.object(sbom, "run") as run, \
                 self.assertRaisesRegex(ValueError, "two-version kernel"):
                sbom.python_inventory("python-kernel-baseline", root, root, root, {})
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
