# Upstream integration — 2026-10-13

## Baseline and scope

- Fork baseline: `072f1d3d` (local master matched origin/master; clean checkout).
- Upstream endpoint: `13e1278b4c46eadede9546d3ada1ff9d94b593dd`.
- Backup: `codex/before-upstream-sync-2026-10-13-072f1d3d`.
- Normal merge, not squash/cherry-pick: all five original commits remain ancestors.
- No GitHub push, Actions dispatch, secrets changes, or release publication performed.

## Integrated commits

| Commit | Change | Integration decision |
|---|---|---|
| `0921a743` | Signed update metadata and verified installer handoff | Keep signature/size/SHA-256 checks; adapt trust and publication to this fork |
| `ccfa714d` | Swedish printer translation | Keep upstream correction |
| `109c39bc` | Suppress identical DRM frames, periodically retry | Keep producer generations, startup probes, validation and fork protections |
| `0b5a3d74` | Version 1.5.1 | Keep dynamic CI version detection; increase Android build number to 69 |
| `13e1278b` | Peer-side auto-login screen check | Keep new protocol field and Windows 7 lock-flag handling; preserve session-scope controls |

## Fork-specific adaptation

- Updates query GitHub Releases for `Elyor1977/rustdesk`, not the upstream version service.
- Release-page and download allowlists accept only this fork. Existing URL tests
  now cover the fork and explicitly reject the original repository.
- The upstream Ed25519 key is not trusted. The public key is embedded with
  `option_env!("RUSTDESK_UPDATE_ED25519_PUBLIC_KEY")` during compilation.
- Missing key disables update checks and rejects verified updates. Invalid key,
  wrong signature, wrong artifact identity or changed bytes fail closed.
- Windows and general Flutter builds receive the public repository variable.
  Windows 7 builds deliberately receive no update key: the common release is
  a Windows 10+ package, not a Windows 7 update channel.
- `Signed release` optionally validates the key pair after environment approval,
  then signs/verifies Windows x64 EXE/MSI metadata before publication.
  `ENABLE_SIGNED_UPDATE_METADATA=true` opts in; existing signing remains usable
  without the new key. Already published metadata/signatures prevent tag reuse.
- Existing fork platform selectors, read-only CI permissions, signing approval,
  unsigned/signed separation, download hashes, Rust/Flutter pins and Android
  concurrency fix remain in place.
- Preserve fallible HTTP-client construction (`?`) when combining the new updater
  with the fork's HTTP client API.
- Preserve macOS atomic cursor seed instead of restoring upstream `static mut`.
- The shared upstream application-name validator allows ASCII underscores.
  Update the existing Windows regression test accordingly; non-ASCII and command
  metacharacters remain rejected.
- No submodule changes. Cargo.lock changes only the two application package versions.
  Flutter dependency lockfile is unchanged after temporary SDK test resolution.

## Verification actually completed

- All workflow YAML checked with actionlint; shellcheck/pyflakes disabled because
  those tools are not available in this local check.
- 7 CI contract tests passed. A new key-propagation test failed before wiring
  the public key and passed afterwards; the existing read-only caller test caught
  upstream publication permissions and passed after preserving caller permissions.
- 7 Windows 7 compatibility/import-library tests passed.
- Update tooling: 15 Python tests, 13 passed and 2 macOS-only tests skipped.
  New compile-time-key support was tested red/green; signer tests also exercise
  signature validation and artifact identity/integrity.
- Pinned CPython 3.12 Linux wheels downloaded with `--require-hashes` successfully:
  cryptography 50.0.0, cffi 2.1.0, pycparser 3.0.
  Local Python tests ran with installed cryptography 50.0.1; Linux CI installs
  the exact pinned versions.
- Rustfmt 1.8.0 from Rust 1.88: all 34 changed Rust files passed. Check tool
  version/output and status; use the matching rustc-driver DLL directory in PATH.
- Locked offline Cargo metadata passed for Windows x64, Linux x64, Android arm64
  and the Windows 7 target. This checks dependency resolution, not compilation.
- Isolated Rust harness compiled the update metadata verifier, artifact validator
  and hash checker. Tests passed with a synthetic Ed25519 key and without a key;
  covered valid signature, tampering, SHA-256 and the Windows app-name validator.
  Harness and synthetic test key are ignored tooling, not release configuration.
- Flutter 3.24.5 analyzer: exit 0, no errors/warnings; 271 informational diagnostics.
- All 136 Flutter tests passed. Initial test startup failed because the temporary
  SDK lacked material fonts; restored the missing cache files from the existing
  same-version SDK, then reran successfully.
- Cargo audit against the cached advisory DB: exit 0, no reported vulnerabilities,
  24 allowed warnings. Advisory DB was not refreshed; this is not a fresh audit.
- `build.py --print-version` reports 1.5.1; diff whitespace check passed.

## Regression surface — existing files and paths changed

Each group below is required by one of the integrated changes. New implementation
files stay in update-specific modules; no unrelated cleanup was intended.

| Existing files | Runtime/build path and reason |
|---|---|
| `src/client.rs`, `src/ui_session_interface.rs`, `libs/base/protos/message.proto`, `src/server/connection.rs`, `src/platform/windows.cc` | New OS-login message and peer-side lock-screen check; prevent OS password typing into an unlocked desktop |
| `src/server/drm_capturer.rs` | Linux DRM frame delivery, duplicate suppression and associated test fixtures |
| `src/common.rs`, `src/updater.rs`, `src/hbbs_http/downloader.rs` | Fork release lookup, metadata trust, bounded/exclusive downloads and verified update flow |
| `src/platform/windows.rs`, `src/platform/macos.rs`, `src/platform/mod.rs`, `src/platform/privileges_scripts/update.scpt` | Platform verification/handoff, MSI errors, macOS transaction/readiness checks and shared safe app-name policy |
| `src/core_main.rs`, `src/main.rs`, `src/service.rs`, `libs/portable/src/main.rs` | Verified EXE/MSI/DMG update entry points and cleanup/handoff plumbing |
| `src/flutter.rs`, `src/flutter_ffi.rs`, `src/ui_interface.rs`, `flutter/lib/desktop/widgets/update_progress.dart` | UI verifies metadata before download, reports errors and cancellation; propagate verified artifact size/hash |
| `src/lib.rs` | Wire new update-specific modules; Rustfmt for the touched module list |
| `src/lang/sv.rs` | Swedish printer translation only |
| `Cargo.toml`, `Cargo.lock`, `libs/portable/Cargo.toml`, `flutter/pubspec.yaml`, `res/PKGBUILD`, `res/rpm*.spec`, `appimage/AppImageBuilder-*.yml` | Align release versions and Android build number |
| `.github/workflows/flutter-build.yml`, `.github/workflows/windows-x64.yml`, `.github/workflows/release.yml` | Metadata capability/key propagation, verified optional publication; preserve existing fork build/signing routes |
| `.github/workflows/ci.yml`, `.github/scripts/test_ci_contract.py` | Run signer regression checks and protect public-key wiring/Windows 7 exclusion |

Resolved workflow conflicts in `flutter-tag.yml` and `playground.yml` retain the
fork versions without a final content change. Windows 7 workflow, native signing
script, `.cargo/config.toml` and Android signed concurrency workflow are unchanged.

## Remaining validation and setup

- Full native RustDesk builds, real Windows 7 loader check, Android installation,
  Windows/macOS auto-login, Linux DRM capture and privileged installer transactions
  have not been exercised locally by this integration.
- Native macOS metadata/offline-update tests and AppleScript tests require macOS.
- User must supply a real Ed25519 seed and public repository variable before
  enabling signed metadata. See `.github/UPDATE-SIGNING.md`.
- Metadata publication currently covers Windows x64 EXE/MSI only. Windows 7,
  Android and other platform packages remain manual installation paths.
- Older peers keep legacy auto-login behavior; the new check needs a capable
  Windows/macOS peer reporting version 1.5.1 or newer.
- This work does not claim to fix the previously reported privacy-mode image
  degradation or monitor reconfiguration error.

## Publish

Push the completed local merge with `git push origin master`; do not force-push.
Run enabled CI/Full Flutter CI and the required platform workflows against the
new master commit. Use a new workflow dispatch rather than rerunning an old commit.
Tag a release only after platform checks pass and signing settings are ready.
