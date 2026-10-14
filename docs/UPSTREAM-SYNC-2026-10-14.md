# Upstream integration: 2026-10-14

## Scope and history

Starting fork: `0083b375`. Reviewed upstream endpoint: `9997b7a3`.
Local backup: `codex/before-upstream-sync-2026-10-14-0083b375`.
No push, pull request, release publication, secret changes or Actions dispatch was performed.

Four original commits were merged, preserving their individual history:

| Commit | Change | Reason |
| --- | --- | --- |
| `07400638` | Keyboard shortcuts, configuration UI and session-specific dispatch | Upstream feature with native/Flutter/Web routing and modifier handling |
| `49a9574f` | DRM producer pacing and libdrmtap 0.5.12 | Match capture rate to encoder demand and panel refresh, without slowing cursor updates |
| `29a160fc` | Floating mouse button delayed-down race | A released, cancelled or disposed press must not later send a remote button-down |
| `76ab280a` | Terminal replay buffer bound | Output without newlines must not grow the replay buffer indefinitely |

Merge commit: `74b07bc5`.

`9997b7a3` removes/reduces tests (94 files, 9,405 deleted lines). Its ancestry is
recorded with an `ours` strategy merge; **its test deletions are not applied**.
This explicitly preserves regression coverage, test-only helpers and Tokio
`test-util`. A zero-behind result refers to ancestry, not an identical source tree.

## Fork-specific conflict resolutions

- `src/ipc/drm.rs`: retain the CPU capture fallback and explicit DMA-BUF error
  handling while applying frame deadlines and demand-based pacing.
- `libs/scrap/src/common/drmtap_dl.rs`: retain existing conversion bindings and add
  the optional exact CRTC refresh binding.
- `src/keyboard.rs`: remove a duplicate import; preserve the platform-gated logger.
- Apply Rust 1.88 formatting to changed Rust files because the fork's CI checks
  those entire files. No unrelated runtime refactor was introduced.

The root `Cargo.lock`, `Cargo.toml`, `.cargo/config.toml`, `hbb_common` submodule,
Windows 7 workflow, Windows/Android signed and unsigned workflows, release and
CI workflows are unchanged from `0083b375`. The quinn-proto 0.11.18 security fix,
fork-specific update trust, signature policy and security tests are retained.

## Dependency review

libdrmtap remains runtime-loaded and SHA-pinned in `build.py`, not a new linked
Rust dependency. Reviewed range:
`95d4d74549631aa5c39461300acfd2e106583cc9..5936a7a88b94aa43516a3dd0eb509d2383f31e2d`.
The range contains 13 commits: exact refresh reporting, framebuffer/context
lifetime fixes, pixel-stride validation, privileged-process environment controls
and associated tests/docs/releases. Native C changes and deployment remain
unverified on this Windows host. An unavailable refresh symbol uses the existing
whole-hertz fallback.

## Verification

- Rustfmt 1.8.0 / Rust 1.88: all 65 changed Rust files passed.
- Flutter 3.24.5 analyzer: exit 0, no errors/warnings; 326 informational diagnostics.
- Flutter unit/widget suite: 199 passed; the browser-only test file is excluded
  by its platform annotation.
- Terminal regression: the previous implementation failed the oversized
  no-newline test; the integrated implementation passed. This used an ignored,
  isolated harness with the exact production buffer implementation, not a full
  RustDesk native build.
- DRM pacing: the upstream arithmetic test passed against extracted exact
  production helpers in an isolated Rust harness, not a Linux capture test.
- CI contract tests: 7 passed. Windows 7 checker tests: 7 passed.
- Actionlint: passed for workflows (external shellcheck/pyflakes disabled).
- Cargo metadata `--offline --locked --no-deps`: passed for Windows x64, Linux
  x64, Android arm64 and Windows 7 x64; this validates manifests, not builds.
- Cargo audit 0.22.0 with refreshed RustSec database `6aed846`: 0 vulnerabilities;
  24 existing warnings (21 unmaintained, 3 unsound). This is not a clean bill of
  health for every dependency and is not a native-library vulnerability audit.
- Final diff whitespace and conflict-marker checks passed.

Local Flutter SDK files required repair before testing. In accordance with the
new upstream AGENTS rule, native bridge generation was not run locally. Two new
wrappers were manually added to the ignored local generated Dart bridge for
analysis/tests; they are not committed. CI regenerates the bridge from Rust.
The temporary Flutter lockfile changes from local SDK resolution were discarded;
the authoritative lockfile is unchanged.

## Regression surface

Existing runtime paths changed only where required by the upstream integration:

- `src/keyboard.rs`, `src/flutter.rs`, `src/flutter_ffi.rs`,
  `src/ui_session_interface.rs`: shortcut interception, loading and explicit
  session routing. Shortcut logic lives in new `src/keyboard/shortcuts.rs`;
  disabled shortcuts and non-Flutter dispatch retain the old forwarding path.
- `src/platform/linux.rs`: query Right Alt's current XKB role before intercepting
  a matching shortcut, to avoid swallowing AltGr input.
- Flutter existing settings/remote pages, toolbar widgets, input/chat/session
  models and native/Web bridge adapters: expose shortcut configuration and route
  session actions. The new shortcut modules own the feature logic.
- `flutter/android/app/src/main/kotlin/com/carriez/flutter_hbb/MainActivity.kt`:
  modifier cleanup on focus loss, necessary for mobile shortcut input.
- `flutter/lib/mobile/widgets/floating_mouse_widgets.dart`: invalidate delayed
  press callbacks after release/cancel/dispose and release only a sent button.
- `src/ipc/drm.rs`, `src/server/drm_capturer.rs`,
  `libs/scrap/src/common/drm_reader.rs`, `drmtap_dl.rs`: DRM producer/consumer
  pacing and optional panel refresh. Non-DRM capture paths are unchanged.
- `src/server/terminal_service.rs`: enforce replay limits for partial lines while
  keeping recent output and the fork's existing UTF-8 protection.
- `build.py` and the comment in `libs/scrap/Cargo.toml`: update only the libdrmtap
  pin/version. `.github/workflows/flutter-build.yml`: add two Linux DRM test
  invocations without changing signing/release policy.
- `src/lang/*.rs`: upstream shortcut UI strings. `.gitignore` and `AGENTS.md`:
  upstream worktree/bridge editing guidance; no application runtime change.

## Still requires CI / device validation

Full native Windows/Android/Linux/Windows 7 builds, regenerated bridge linkage,
physical keyboard/modifier/session switching, Android floating-button behavior,
Linux DRM DMA-BUF and CPU fallback, and signed release installation were not
executed here. The browser-only mouse regression stalled while loading Chrome;
it was stopped and is **not reported as passed**.

Upload the local commits with `git push origin master`. Then check the fork's CI,
Full Flutter CI and platform builds. Do not infer successful device behavior
solely from the local analyzer or isolated tests.
