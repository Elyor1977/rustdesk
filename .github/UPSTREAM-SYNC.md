# Upstream integration: 2026-09-28

## History

- Previous fork master: `7078b346b7d0e1ce02ea5f2d1a462d25cfc6f815`.
- Local recovery branch: `backup/master-before-upstream-2026-09-28`.
- Previous upstream base: `0b3a1ddd80285c87baad495f79b54d19ef3ba4d9`.
- New upstream base: `4812a9815bd3c6a93f3ad903f29504168c4930a1`.
- All 45 upstream commits are ancestors of the updated branch. The fork keeps
  four thematic commits, not 45 duplicated cherry-picks or a squash of upstream.
- Tags, remote branches, secrets and GitHub settings were not changed.

## Integration decisions

- Preserve fork request/login bounds, expiry and eviction, atomic state,
  safe macOS update handling, dependency pins and release controls.
- Keep Windows and Android signed/unsigned workflows separate. Existing fork
  workflow files are unchanged except `flutter-build.yml`, which receives
  upstream cursor/DRM tests and bounded AppRun packaging.
- Use upstream clipboard range validation, overflow handling and served-list
  checks; these supersede the older fork range clamp without silently truncating
  oversized requests.
- Keep upstream bounded Windows absolute mouse coordinates and the fork's
  `FormatMessage` buffer bounds fix together.
- Keep upstream macOS cursor-seed identity with the fork's atomic seed storage.
- Keep upstream KX v1 decoding, signed parameters and WebSocket protections with
  the fork's mandatory secure-TCP handling and direct loopback test helpers.
- Pin `clipboard-master` to upstream's `522fafb65edfe7939cf63fa797f916569ecab595`:
  its readiness API is required by the new initial clipboard synchronization.
- Update WebRTC and tungstenite pins to the exact upstream revisions. Keep the
  fork's other pins and platform dependency replacements.
- Update `libs/hbb_common` to `229b904508364c8997aad0fb5af57effac859f60`, exactly
  the parent upstream commit's pointer, not the submodule's latest branch.

## Regression surface

All upstream runtime changes are intentional parts of this synchronization:

| Existing files / areas | Changed runtime path and reason |
| --- | --- |
| `src/client.rs`, `src/common.rs`, `src/server/connection.rs`, `libs/hbb_common` | KX negotiation, signed parameters, encrypted WebSocket frames and unauthenticated message limits; retain fork authentication protections. |
| `src/client/io_loop.rs`, `src/clipboard*.rs`, `src/server/clipboard_service.rs`, `libs/clipboard/src/platform/unix/*`, `libs/clipboard/src/windows/wf_cliprdr.c` | Initial clipboard synchronization, permission checks, transfer ranges, FILETIME and Finder completion fixes. |
| `src/flutter*.rs`, `src/server/input_service.rs`, `src/platform/macos.rs`, Flutter cursor/model/native/web files, `libs/base/protos/message.proto` | Cursor validation, sizing, identity, binary delivery and bounded decoded caches. |
| `src/ipc*.rs`, `src/ipc/drm.rs`, `src/server/{display_service,drm_capturer,uinput,wayland}.rs`, `libs/scrap/src/common/{drm_reader,drmtap_dl}.rs` | DRM rotation, hotspot detection, coordinate mapping and single-thread uinput range updates. |
| `libs/scrap/src/dxgi/*`, `libs/scrap/src/common/vram.rs` | Windows HDR tone mapping and AMD-only stall detection. |
| `libs/enigo/src/win/win_impl.rs`, `flutter/windows/runner/main.cpp` | Bounded mouse coordinates and permission to foreground an existing session. |
| `src/platform/mod.rs`, `src/ui/remote.rs`, `src/ui/remote.tis`, `src/ui_session_interface.rs`, Flutter terminal models | Mobile reverse scrolling and terminal alternate-screen trackpad behavior. |
| `src/server.rs`, `src/ui/cm.tis`, Flutter server page, `libs/base/src/config/keys.rs` | Temporary password rotation timing and optional elevation-button hiding. |
| `src/hbbs_http/sync.rs`, `src/common.rs` | Throttled heartbeat/proxy diagnostics. |
| `src/lang.rs`, changed `src/lang/*.rs`, Ukrainian README | Upstream translations and distinct Portuguese locale identifiers. |
| `build.py`, `.github/workflows/flutter-build.yml`, manifests/lockfile, AppImage scripts | Required dependency/API alignment, new upstream tests and bounded AppRun argument splitting. |

Integration-only changes beyond upstream plus the existing fork patches:

- `src/common.rs`: adapt three new tests to the fork's `SocketAddr` helper.
- `src/client.rs`, `src/client/io_loop.rs`: new loopback tests open direct TCP
  sockets so global proxy/WebSocket settings cannot redirect them.
- Changed Rust files are formatted with Rust 1.88 rustfmt, matching the fork CI
  check. Formatting does not intentionally change runtime behavior.
- No unrelated runtime refactoring or feature changes were added during review.

## Verification

- Rust 1.88 rustfmt check on Rust files changed since previous master: passed.
- actionlint on GitHub workflows: passed (shellcheck/pyflakes unavailable).
- YAML parsing, Cargo.lock TOML parsing, Python build-script syntax: passed.
- `cargo metadata --locked --format-version 1 --filter-platform
  x86_64-pc-windows-msvc` with Rust 1.88: passed without changing `Cargo.lock`.
  A temporary short-path mapping was needed for Cargo's nested dependency cache
  on Windows; it was removed after verification.
- `python build.py --print-version`: `1.5.0`.
- `git diff --check` on integration edits, conflict-marker scan and submodule
  checkout consistency: passed. The full upstream range reports blank context
  lines in `appimage/apprun-split-arguments.patch`; their leading spaces are
  required patch syntax and were preserved.
- Full Rust/Flutter compilation, native tests and signed artifacts still require
  CI: this workstation has no Flutter SDK or MSVC C++ build components.

Review used the local `code-reviewer` skill, especially bounds, shared state,
dependency changes and conflict-resolution checks. This is not a claim of a
complete security audit or successful end-to-end builds.

## Publish and future updates

Push the recovery branch before replacing remote master. Use an explicit lease
against the previously checked remote SHA; if it fails, inspect new remote work
instead of using an unconditional force push. Do not pull the old history back
into the rebased branch.

```powershell
git push origin backup/master-before-upstream-2026-09-28
git push --force-with-lease=refs/heads/master:7078b346b7d0e1ce02ea5f2d1a462d25cfc6f815 origin master
```

Future upstream-only commits are visible without counting fork commits:

```powershell
git fetch upstream
git log --oneline master..upstream/master
git rev-list --left-right --count upstream/master...master
```

The last command prints `behind ahead`; immediately after this integration it
should be `0 4` against the recorded upstream revision. New upstream pushes can
increase the first number. Run CI plus Windows/Android unsigned builds before
creating a new signed release tag. Existing tags still name their original code.
