# Upstream integration: 2026-10-05

Fork baseline: `0b73e100ca8b9b300cae3899f4406f47c9d9f79f`.
Upstream endpoint: `c9c0b5d0efd44b364b31639f3c118e8adc42d98c`.
Local backup: `codex/before-upstream-sync-2026-10-05-0b73e100`.

## Integrated commits

- `685fa2e4`: Linux DRM startup cache warming no longer wakes sleeping displays.
- `5406950b`: macOS Configure opens the Screen Recording settings pane.
- `c9c0b5d0`: Android voice-call permission prompt uses the correct translation key.

Normal merge retains the three original commits and all existing fork commits.
The only content conflict was the cache-warming block in
`src/server/drm_capturer.rs`; upstream's generation check and `wake: false`
were retained. Rustfmt adjustments are limited to the integrated lines and
the trailing blank line in `src/lang/ur.rs`.

## Verification

- Flutter 3.24.5 / Dart 3.5.4: `flutter pub get` completed.
- `flutter analyze --no-fatal-infos`: success; 271 informational findings,
  no warnings or errors.
- `flutter test`: all 136 tests passed locally on Windows.
- Five CI contract tests and seven Windows 7 checker tests passed.
- Actionlint passed; changed Rust files passed the exact CI rustfmt command.
- Android's prompt key matches all 53 changed language files. The same
  key-alignment check fails against the pre-merge Android source.
- CI, signing, Windows 7 configuration, Cargo manifests/lockfile, Flutter
  manifest/lockfile and submodule revisions are unchanged from the fork baseline.
- Security review retained DRM authorization before the handshake, connection
  limits and session-change checks. No new secrets or dependencies were added.

## Regression surface and remaining checks

- `src/ipc.rs`, `src/ipc/drm.rs`, `src/server/drm_capturer.rs`,
  `src/server/connection.rs`: Linux DRM handshake, startup probing and login
  settlement change together. Update the installed service and app together.
- `src/server/wayland.rs`: upstream comment update only.
- `flutter/lib/desktop/pages/desktop_home_page.dart`: macOS Screen Recording
  Configure action opens system settings; other platform branches are unchanged.
- Android `AudioRecordHandle.kt` and `src/lang/*.rs`: prompt key and translations.

No full native Rust/Android/macOS/Windows 7 build or hardware runtime test was
performed locally. Linux DRM wake/no-wake behavior and the macOS settings action
still need platform testing. Existing Flutter tests do not exercise these OS
integrations. Repository-wide `cargo fmt --all -- --check` fails on unrelated
pre-existing formatting and missing generated `src/ui/inline.rs`; CI checks
changed files instead, and that check passed. GitHub workflows were not started
and changes were not pushed by the agent.
