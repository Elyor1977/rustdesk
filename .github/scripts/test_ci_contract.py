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
    def test_tls_audit_exemption_requires_a_verified_roots_graph(self):
        steps = workflow("ci")["jobs"]["cargo_audit"]["steps"]
        command = next(step["run"] for step in steps if step.get("name") == "Run cargo audit")
        self.assertLess(command.index("python3 .github/scripts/check_tls_roots.py"),
                        command.index("cargo audit --ignore RUSTSEC-2026-0381"))

    def test_fdroid_locks_build_dependencies_not_the_patched_bridge(self):
        source = (ROOT / "flutter/build_fdroid.sh").read_text(encoding="utf-8")
        prebuild, build = source.split("\nbuild)\n", 1)
        self.assertIn("flutter packages pub get\n", prebuild)
        self.assertNotIn("pub get --enforce-lockfile", prebuild)
        self.assertIn("flutter packages pub get --enforce-lockfile", build)

    def test_platform_rust_checks_skip_retained_interactive_tests(self):
        jobs = workflow("flutter-build")["jobs"]
        checks = [step for job in jobs.values() for step in job.get("steps", [])
                  if step.get("name") == "Run the Rust tests"]
        self.assertEqual(len(checks), 2)
        for step in checks:
            command = next(line for line in step["run"].splitlines()
                           if "cargo test" in line and "--lib" in line)
            self.assertIn("--skip test_get_cursor_pos", command)
            self.assertIn("--skip test_get_key_state", command)

    def test_fork_update_public_key_reaches_desktop_builds(self):
        for name, value in (
            ("windows-x64", "${{ !inputs.windows-7 && vars.RUSTDESK_UPDATE_ED25519_PUBLIC_KEY || '' }}"),
            ("flutter-build", "${{ vars.RUSTDESK_UPDATE_ED25519_PUBLIC_KEY }}"),
        ):
            with self.subTest(workflow=name):
                self.assertEqual(workflow(name)["env"].get(
                    "RUSTDESK_UPDATE_ED25519_PUBLIC_KEY"),
                    value)

    def test_android_signing_caller_does_not_lock_its_build(self):
        caller = workflow("android-signed")["concurrency"]["group"]
        build = workflow("android")["concurrency"]["group"]
        build = build.replace("${{ inputs.release && 'signed' || 'unsigned' }}",
                              "signed")
        for arch in workflow("android-signed")["on"]["workflow_dispatch"]["inputs"]["arch"]["options"]:
            with self.subTest(arch=arch):
                self.assertNotEqual(
                    caller.replace("${{ inputs.arch }}", arch).lower(),
                    build.replace("${{ inputs.arch || 'aarch64' }}", arch).lower())

    def test_flutter_analysis_keeps_errors_and_warnings_fatal(self):
        steps = workflow("flutter-ci")["jobs"]["flutter-analyze"]["steps"]
        analyze = next(step for step in steps if step.get("name") == "flutter analyze")
        self.assertEqual(analyze["run"], "flutter analyze --no-fatal-infos")
        self.assertNotEqual(analyze.get("continue-on-error"), "true")
        tests = next(step for step in steps if step.get("name") == "flutter test")
        self.assertEqual(tests["run"], "flutter test")
        self.assertNotEqual(tests.get("continue-on-error"), "true")

    def test_flutter_build_accepts_read_only_callers(self):
        config = workflow("flutter-build")
        self.assertNotIn("permissions", config)
        for name, job in config["jobs"].items():
            with self.subTest(job=name):
                self.assertNotEqual(job.get("permissions", {}).get("contents"),
                                    "write")
        self.assertEqual(workflow("flutter-ci")["permissions"]["contents"], "read")
        self.assertEqual(workflow("flutter-nightly")["permissions"]["contents"],
                         "write")
        for event in ("push", "pull_request"):
            self.assertIn(".github/workflows/flutter-build.yml",
                          workflow("flutter-ci")["on"][event]["paths"])

    def test_signing_has_separate_noncancelling_concurrency(self):
        for name in ("windows-x64", "android"):
            with self.subTest(workflow=name):
                concurrency = workflow(name)["concurrency"]
                self.assertIn("inputs.release", concurrency["group"])
                self.assertIn("!inputs.release", concurrency["cancel-in-progress"])
        steps = workflow("android")["jobs"]["build-android"]["steps"]
        apk_step = next(step for step in steps if step.get("name") == "Build apk")
        for name, value in apk_step["env"].items():
            if name.startswith("ANDROID_") and "secrets." in value:
                self.assertIn("inputs.release &&", value)

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
