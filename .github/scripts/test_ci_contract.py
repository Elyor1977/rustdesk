import os
from pathlib import Path
import subprocess
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    relative = f".github/workflows/{name}.yml"
    baseline = os.environ.get("CI_CONTRACT_BASELINE")
    if baseline:
        source = subprocess.check_output(
            ["git", "show", f"{baseline}:{relative}"], cwd=ROOT, text=True)
    else:
        source = (ROOT / relative).read_text(encoding="utf-8")
    return yaml.load(source, Loader=yaml.BaseLoader)


class WorkflowContractTests(unittest.TestCase):
    def test_signing_has_separate_noncancelling_concurrency(self):
        for name in ("windows-x64", "android"):
            with self.subTest(workflow=name):
                concurrency = workflow(name)["concurrency"]
                self.assertIn("inputs.release", concurrency["group"])
                self.assertIn("!inputs.release", concurrency["cancel-in-progress"])

    def test_signing_requires_successful_checks_before_approval(self):
        for name in ("release", "windows-signed", "android-signed"):
            with self.subTest(workflow=name):
                jobs = workflow(name)["jobs"]
                self.assertEqual(jobs["approve"]["needs"], "checks")
                self.assertEqual(jobs["checks"]["uses"],
                                 "./.github/workflows/release-checks.yml")
        jobs = workflow("release")["jobs"]
        self.assertEqual(jobs["checks"]["needs"], "validate")
        checks = workflow("release-checks")["jobs"]
        for name in ("rust", "flutter"):
            self.assertEqual(checks[name]["with"]["check-context"], "release")

    def test_automatic_flutter_checks_have_bridge_without_full_build(self):
        config = workflow("flutter-ci")
        self.assertIn("push", config["on"])
        self.assertIn("pull_request", config["on"])
        self.assertIn("workflow_call", config["on"])
        jobs = config["jobs"]
        self.assertIn("workflow_dispatch", jobs["run-ci"]["if"])
        self.assertIn("Full Flutter CI", jobs["run-ci"]["if"])
        self.assertEqual(jobs["run-ci"]["with"]["publish-release"], "false")
        self.assertEqual(jobs["flutter-analyze"]["needs"], "generate-bridge")
        restores = [step for step in jobs["flutter-analyze"]["steps"]
                    if step.get("uses", "").startswith("actions/download-artifact@")]
        self.assertEqual(restores[0]["with"]["name"],
                         "bridge-artifact-checks-${{ github.run_id }}")
        android = workflow("android")["jobs"]
        self.assertEqual(android["generate-bridge"]["with"]["artifact-suffix"],
                         "-android")
        windows = workflow("windows-x64")["jobs"]
        self.assertIn("windows", windows["generate-bridge"]["with"]["artifact-suffix"])


if __name__ == "__main__":
    unittest.main()
