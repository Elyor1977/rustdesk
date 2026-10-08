# Upstream integration: 2026-10-08

Fork baseline: `c8f305acde3d5e4192e9b87972dff961cc7194ef`.
Upstream endpoint: `6da7977a`.
Local backup: `codex/before-upstream-sync-2026-10-08-c8f305ac`.

## Changes and integration decisions

- `25d2c6db`: macOS keyboard-release/text-injection failure diagnostics, throttled
  at five-second intervals. New messages contain neither typed text nor key codes.
- `6da7977a`: defer macOS refresh after feeding a non-latency-free hardware encoder
  until its first packet. This prevents VideoToolbox warm-up from restarting forever.
  Existing encoder-failure fallback remains unchanged. Windows, Android and Linux
  retain the original refresh policy.

Normal merge retains both upstream commits. Two conflicts were resolved:

- `src/server/input_service.rs`: retain the fork's `lock_virtual_input()` mutex
  access; add the missing-input diagnostic without restoring upstream unsafe state.
- `Cargo.lock`: retain explicit revision pinning and regenerate with Cargo.
  Both rdev manifests now pin `0904f23ce496e255461a98848b85c11fa5a62eab`.
  The inspected range contains three diagnostic commits and their merge; only
  macOS source changes. No other locked package changed.

Two existing line-wrap issues in the touched Enigo file were normalized because
the fork CI checks the whole modified Rust file. No input behavior changed there.

## Verification

- Skills: ponytail, code-review-and-quality, test-driven-development,
  security-and-hardening, debugging-and-error-recovery, OCR delegation preview.
- Manual review covers all six existing changed files, including the lockfile
  excluded by OCR extension filtering. No file skipped; no blocking findings.
  OCR rule retrieval was blocked by automatic safety review; no external review
  service was called and the block was not bypassed.
- Isolated compiled Rust refresh-policy tests: the prior unconditional policy
  fails macOS assertions; the new policy passes both macOS-conditioned and Windows
  runs, including all eight flag combinations. The tested expression matches
  production. These tests do not exercise an actual macOS encoder or video loop.
- `cargo check --locked --offline -p rdev`: passed on Windows.
- Rustfmt of all three changed source files and actionlint passed.
- Five CI contract tests and seven Windows 7 checker tests passed.
- Flutter 3.24.5 analyzer: no warnings/errors, 271 informational findings;
  all 136 Flutter tests passed. Pub get generated SDK-compatible test dependency
  resolution locally; generated Flutter lockfile changes were discarded.
- Cargo audit 0.22.0 with refreshed RustSec database: exit 0 under the existing
  policy, with 24 allowed warnings. This is not a claim of zero advisories.
- CI, signing, Windows 7 configuration, Flutter source/lockfile and submodules
  remain unchanged from the fork baseline.

## Regression surface and limits

- `src/server/video_service.rs`: hardware-encoder warm-up/refresh on macOS;
  both frame-processing calls pass the new local flag. Other OS refresh decisions
  are unchanged; this does not fix Windows privacy-mode image quality.
- `src/server/input_service.rs`, `libs/enigo/src/macos/macos_impl.rs`:
  macOS failure diagnostics; existing fork synchronization remains intact.
- `Cargo.toml`, `libs/enigo/Cargo.toml`, `Cargo.lock`: one pinned dependency update
  needed to include the upstream rdev diagnostics reproducibly.

Full Rust unit-test compilation stopped at kcp-sys bindgen because libclang is
absent locally. No full native build, macOS keyboard/VideoToolbox runtime test,
Windows 7 runtime test, Android build or signing operation was performed.
No GitHub workflow was started and no changes were pushed by the agent.
