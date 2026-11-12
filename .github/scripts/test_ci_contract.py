import fnmatch
import os
import re
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
    def test_legacy_manual_builds_cannot_sign_or_publish(self):
        for name in ("flutter-nightly", "playground"):
            config = workflow(name)
            with self.subTest(workflow=name):
                self.assertEqual(config["permissions"]["contents"], "read")
                self.assertNotRegex(str(config), r"secrets\.(?:ANDROID_|WINDOWS_CERTIFICATE|MACOS_|SIGN_)")
                for job in config["jobs"].values():
                    self.assertNotIn("secrets", job)
                    if "uses" in job:
                        self.assertEqual(job["with"]["publish-release"], "false")
                    self.assertFalse(any("action-gh-release@" in step.get("uses", "")
                                         for step in job.get("steps", [])))

    def test_unsigned_android_packages_have_artifact_routes(self):
        jobs = workflow("flutter-build")["jobs"]
        for name in ("build-rustdesk-android", "build-rustdesk-android-universal"):
            with self.subTest(job=name):
                uploads = [step for step in jobs[name]["steps"]
                           if step.get("uses", "").startswith("actions/upload-artifact@")
                           and step["with"].get("path") == "signed-apk/*.apk"]
                self.assertEqual(len(uploads), 1)
                self.assertEqual(uploads[0]["if"],
                                 "env.ANDROID_SIGNING_KEY == '' && env.UPLOAD_ARTIFACT == 'true'")
                self.assertEqual(uploads[0]["with"]["if-no-files-found"], "error")

    def test_platform_builds_cover_native_build_inputs(self):
        paths = ("build.rs", ".cargo/config.toml", "vcpkg.json",
                 "res/vcpkg/mfx-dispatch/portfile.cmake",
                 ".github/workflows/bridge.yml",
                 ".github/patches/flutter_3.24.4_dropdown_menu_enableFilter.diff")
        for name in ("windows-x64", "android"):
            for event in ("push", "pull_request"):
                patterns = workflow(name)["on"][event]["paths"]
                for path in paths:
                    with self.subTest(workflow=name, event=event, path=path):
                        self.assertTrue(any(fnmatch.fnmatchcase(path, pattern)
                                            for pattern in patterns))

    def test_windows_tests_and_signer_preflight_precede_signing(self):
        steps = workflow("windows-x64")["jobs"]["build-windows-x64"]["steps"]
        names = [step.get("name") for step in steps]
        tests = next(step for step in steps if step.get("name") == "Run the Rust tests")
        self.assertIn("!inputs.windows-7", tests["if"])
        self.assertIn("--lib --features flutter,hwcodec,vram", tests["run"])
        self.assertIn("-p clipboard -p base", tests["run"])
        self.assertIn("-p webrtc-dtls", tests["run"])
        self.assertLess(names.index("Run the Rust tests"), names.index("Sign application files"))
        self.assertLess(names.index("Validate signing configuration"),
                        names.index("Install vcpkg dependencies"))
        preflight = steps[names.index("Validate signing configuration")]
        self.assertIn("-ValidateOnly", preflight["run"])

    def test_android_signer_preflight_precedes_native_build(self):
        steps = workflow("android")["jobs"]["build-android"]["steps"]
        names = [step.get("name") for step in steps]
        self.assertLess(names.index("Validate Android signing configuration"),
                        names.index("Install vcpkg dependencies"))
        build = steps[names.index("Build apk")]
        self.assertNotIn("key.properties", build["run"])
        self.assertIn("inputs.release", build["env"]["ANDROID_KEY_STORE_FILE"])
        gradle = (ROOT / "flutter/android/app/build.gradle").read_text(encoding="utf-8")
        for name in ("ANDROID_KEY_STORE_FILE", "ANDROID_ALIAS",
                     "ANDROID_KEY_STORE_PASSWORD", "ANDROID_KEY_PASSWORD"):
            self.assertIn(f"System.getenv('{name}')", gradle)
            self.assertIn(name, build["env"])

    def test_single_sdk_callers_only_generate_the_required_bridge(self):
        bridge = workflow("bridge")
        self.assertEqual(bridge["on"]["workflow_call"]["inputs"]["include-modern"]["default"], "true")
        matrix = bridge["jobs"]["generate_bridge"]["strategy"]["matrix"]
        self.assertIn("inputs.include-modern", matrix["flutter-version"])
        for name in ("windows-x64", "android", "flutter-ci"):
            with self.subTest(workflow=name):
                self.assertEqual(workflow(name)["jobs"]["generate-bridge"]["with"]["include-modern"], "false")

    def test_auth_diagnostics_are_throttled_and_metadata_only(self):
        allowed = {"self.inner.id()", "self.authorized",
                   "!lr.password.is_empty()", "result.is_ok()"}
        for relative, expected in (("src/client.rs", 2),
                                   ("src/client/io_loop.rs", 3),
                                   ("src/server/connection.rs", 8)):
            source = (ROOT / relative).read_text(encoding="utf-8")
            sites = re.findall(
                r'hbb_common::throttled_log!\(\s*Duration::from_secs\(1\),\s*debug,\s*'
                r'"\[auth-diag\][^"\n]*"(.*?)\);', source, re.DOTALL)
            self.assertEqual(len(sites), expected, relative)
            self.assertEqual(source.count("[auth-diag]"), expected, relative)
            for arguments in sites:
                self.assertTrue({part.strip() for part in arguments.split(",")
                                 if part.strip()} <= allowed, relative)

    def test_android_input_has_unique_top_level_constants(self):
        source = (ROOT / "flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/InputService.kt").read_text(encoding="utf-8")
        names = re.findall(r"^const val (\w+)\b", source, re.MULTILINE)
        self.assertEqual(len(names), len(set(names)),
                         "Duplicate Kotlin constants prevent APK compilation")

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
                         "read")
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
