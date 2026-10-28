# Upstream integration — 2026-10-28

## Scope and history

- Fork baseline: `0a6c93a4`; backup: `codex/backup-before-upstream-2026-10-28`.
- Integrated upstream tip: `04360797addc71138ea30e6c630c073811d9a1d5`.
- Merge commit: `83dd2ef3`, retaining the ten original upstream commits.
- No push, workflow dispatch, tag, release, installed-client change, or secret change.
- The user's untracked `PktMon.etl` is not part of this integration.

## Integrated upstream changes

| Commit | Change |
| --- | --- |
| `f96a44a0` | Mozilla TLS roots 1.0.11 |
| `182356ee` | Desktop peer loading without APP_DIR |
| `a5e98640` | Dutch translations |
| `59f2953c` | Explicit privacy-mode-1 broker executable and quoted argv[0] |
| `eb239024` | Translation placeholder and meaning corrections |
| `894f5328` | Portuguese API connection hints |
| `d0a1af8c` | Android Storage Access Framework file transfers |
| `350966b3` | Trusted-device V2, expiration, revocation, legacy migration |
| `bb8083cb` | hbb_common trusted-device persistence and UDP send recovery |
| `04360797` | Dutch translations |

`libs/hbb_common` is exactly upstream `fae47e024dd83cef6aaecde0aa7d11731df11649`.
Its range from `edefa08b` changes only configuration persistence and UDP sending;
no private submodule commit is required.

## Conflict decisions and regression surface

- `libs/base/src/fs.rs`: keep no-follow writes, sticky write errors, recoverable
  overwrite confirmation, failed-resume rejection, and symlink-safe empty-directory
  removal. Dispatch SAF paths before filesystem metadata checks. Retain SAF's own
  terminal provider-error handling instead of applying ordinary-file resume recovery
  to a document stream. Existing file and download regressions remain enabled.
- `src/client.rs`: prepare trusted-device credentials before the instrumented send;
  retain secret-free markers and propagate the new Result to upstream callers.
- `src/client/io_loop.rs`: let V2 process the response before existing UI handling;
  retain diagnostics, but do not reuse the consumed LoginResponse or restore the old
  trust flag assignment over the V2 result.
- `src/server/connection.rs`: retain password/login diagnostics and call the V2
  authorization hook after accepted permanent-password authentication.
- SAF also necessarily changes Kotlin document providers, mobile file-manager UI,
  file models, JNI initialization, and file-transfer routing in `src/common.rs`,
  `src/ipc/fs.rs`, `src/ui_cm_interface.rs`, and `src/server/connection.rs`.
- V2 necessarily changes the login protobuf, authentication/configuration IPC,
  `src/auth_2fa.rs`, settings/management dialogs, service transitions, configuration
  synchronization, and new `src/trusted_devices/` modules. This is an authentication
  migration, not a proposed fix for the observed corporate-network TCP resets.
- `src/flutter_ffi.rs` changes peer loading and exposes the upstream trust manager.
  The committed Web bridge includes the new renewal method. Native bridge codegen
  was NOT run; the ignored local Dart wrapper was updated by hand for analysis/tests.
- Other runtime changes are the isolated privacy-mode-1 process-launch correction,
  translations, the TLS store, and hbb_common's direct UDP send path.
- Changed Rust files were formatted with the CI-pinned Rust 1.88 because the incoming
  upstream code otherwise fails this fork's changed-file formatting gate.
- Existing `.github/`, `.cargo/`, and `flutter/windows/` files are unchanged from the
  fork baseline: signing, CI policy, and Windows 7 build configuration are retained.

## Compression dependency follow-up

The refreshed RustSec database (2026-10-28, commit
`40f5be6fb12ed93fc591bf4ab23b7d793b3f2239`) reported two blocking findings on the
baseline: RUSTSEC-2026-0403 in zstd-safe 7.1.0 and RUSTSEC-2026-0410 in zstd-sys.
The first affects legacy streaming write decompression; the second is wasm32-only.
Neither is treated as a proven explanation for the native TCP connection failure.

The separate follow-up uses official zstd 0.14.3, zstd-safe 8.2.0 and
zstd-sys 2.1.2+zstd.1.5.7. A one-line re-export under `libs/zstd-compat` retains
the existing 0.13.1 dependency requirement without editing hbb_common. Its version
is `0.13.1+rustdesk.1`, explicitly identifying compatibility rather than the upstream
0.13.3 implementation. HTTP compression-codecs/core are updated within their 0.4
ranges so they do not retain a second vulnerable zstd-safe. No zstd audit exemption
is added. See the adapter README for provenance and removal criteria.

## Verification and limits

- Flutter 3.24.5 analysis: exit 0, no errors or warnings; 329 informational findings.
- Full Flutter suite: 217 passed, one pre-existing skipped test.
- `base`: 28 passed, three pre-existing Windows symlink-privilege ignores.
- `hbb_common --features webrtc`: 136 passed, including UDP recovery and configuration.
- zstd compatibility: two tests passed. The legacy corrupt-frame test first failed
  with the old implementation (output position 1024 instead of 0).
- CI contract checks: 12 passed; TLS guard tests: two passed; TLS guard passed.
- Windows 7 checker tests: seven passed. This is not a Windows 7 device boot test.
- Update metadata tooling: 13 passed, two pre-existing platform skips.
- Rustfmt 1.88 changed-file checks and `git diff --check`: passed.
- RustSec audit with the existing policy: zero blocking vulnerabilities; 24
  unmaintained and three unsound informational findings remain. They are not newly
  suppressed or claimed fixed by this integration.
- Root `cargo check --locked --lib --features flutter` was attempted and stopped in
  native dependencies: missing VCPKG_ROOT (scrap) and libclang (kcp-sys). It did NOT
  establish compilation of the new root authentication modules or run their tests.
- Linux-only SAF descriptor/provider regressions, Android device/provider behavior,
  Windows/macOS full builds, signing, Windows 7 execution, trusted-device migration
  across installed clients, and real remote sessions remain unverified locally.
  The existing CI and subsequent device tests must validate these before release.

Raw local evidence is under `target/integration-tools/sync-2026-10-28-*` and is
intentionally not committed. Review used TDD, minimal-diff and security checks;
passing local subsets is not represented as a complete signed-release validation.
