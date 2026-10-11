# Upstream integration: 2026-10-11

Fork baseline: `036d6f0caa567461f3366e6c9528e150a37bed99`.
Upstream endpoint: `c8532719c0cfc497c64b9f1e0bc9d981db9137db`.
Local backup: `codex/before-upstream-sync-2026-10-11-036d6f0c`.

## Changes

- `1d4abd02`: reqwest 0.12.28 fixes HTTP API authentication through HTTPS proxies.
- `9b9e5f11`: reconcile PipeWire stream position with the only matching output.
- `3f4bfe53`: layout-aware Wayland keyboard input, modifier ownership and release.
- `0bc2473f`: advertise DRM frame dimensions after hardware plane rotation.
- `001b0e96`: preserve the user's deletion of the Windows virtual printer on upgrade.
- `67090d3a`: failed privacy requests cannot turn off another connection's mode;
  successful activation closes other remote-control connections, not file transfers.
- `4411d10f`: identify the logged-in process user inside Flatpak.
- `c8532719`: forward the release of a previously pressed desktop/web mouse button
  even when cursor-control ownership changes.

## Conflict resolutions and preservation

- `Cargo.toml`: retain the fork's `uzers` replacement alongside the two new Linux
  dependencies. No unrelated dependency upgrade or floating Git reference added.
- `Cargo.lock`: resolve merge markers, then regenerate with Cargo 1.88.0. Preserve
  fork Git revisions and dependency patches. Cargo rebinds Windows dependencies
  to the existing patched versions and removes the unused windows-sys 0.61.2 entry.
- `src/server/drm_capturer.rs`: accept the new plane-rotation dimension calculation;
  retain fork generation checks, capture validation and non-waking startup probes.
- `src/server/uinput.rs`: accept layout-aware input while retaining error propagation
  for ordinary key-down IPC failures. Both paths use the throttled diagnostic.
- CI, signing configuration, Windows 7 configuration and all submodule pointers
  remain unchanged. Original upstream commits are retained by a normal merge;
  master history is not rewritten or squashed.

## Regression surface

- `Cargo.toml`, `Cargo.lock`: proxy HTTP behavior and Linux keyboard dependencies.
- `libs/scrap/src/wayland/pipewire.rs`: multi-monitor stream position reconciliation;
  unknown or ambiguous resolutions retain their original position.
- `src/server/uinput.rs`, `src/server/input_service.rs`, `src/ipc.rs`: Linux character
  mapping and IPC error reporting. New layout modules own discovery and cache state.
- `flutter/lib/models/input_model.dart`: Legacy character release and desktop/web
  mouse-button release tracking. `flutter/lib/mobile/pages/remote_page.dart` receives
  only an upstream comment documenting an existing IME limitation.
- `libs/scrap/src/common/drm_reader.rs`, `src/ipc/drm.rs`,
  `src/server/drm_capturer.rs`: rotated DRM display enumeration and frame sizing.
- `flutter/lib/desktop/pages/install_page.dart`, `libs/remote_printer/src/setup/printer.rs`,
  `src/platform/windows.rs`, `res/msi/CustomActions/{CustomActions.def,RemotePrinter.cpp}`,
  `res/msi/Package/Fragments/ShortcutProperties.wxs`: detect the actual printer before
  update and preserve explicit installation choices.
- `src/privacy_mode.rs`, `src/server/connection.rs`: privacy ownership during failure
  cleanup and closure of competing remote-control connections.
- `src/platform/linux.rs`: Flatpak-only active username lookup.

These paths implement the eight requested fixes. No unrelated runtime refactoring
is included. Manual review uses minimal-change, code-review, security and testing
skills; concise reporting uses caveman. No external AI review service is called.

## Verification and limits

- Cargo 1.88.0 locked dependency metadata: Windows x64, Linux x64 and Android arm64 pass.
- Rust 1.88.0 changed-file formatting: pass.
- Five CI contract tests and seven Windows 7 checker tests: pass.
- Conflict-marker and whitespace checks: pass.
- Flutter 3.24.5 analyzer (`--no-fatal-infos`): exit 0, no errors or warnings.
  Existing informational findings are not treated as errors by the fork CI.
- All 136 Flutter tests pass. The SDK carries the same dropdown patch as CI.
  Pub get generated SDK-compatible test dependency resolution locally; those
  generated `flutter/pubspec.lock` changes are discarded, not integrated.
- No full native build or new Cargo audit run was performed; CI must run the
  existing RustSec gate before release. Metadata does not establish API compatibility.

Metadata is not a native build. Linux Wayland keyboard/DRM, Windows privacy mode,
MSI upgrade, Windows 7 execution, authenticated HTTPS proxy and mobile end-to-end
behavior still require platform testing. Upstream's keyboard change has no permanent
regression tests; its Xwayland freshness and multi-seat limitations remain. The
reported Windows privacy-mode image blur is not claimed fixed by this integration.
No release signing, GitHub workflow execution or push is performed by the agent.

## Publish

After checking the local result, run `git push origin master`. Do not force-push.
Run CI, Full Flutter CI, Windows unsigned and Android unsigned before signed release;
also run Linux unsigned for the new Wayland/DRM paths. Existing tags keep naming
their previous code.
