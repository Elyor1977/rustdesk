# Upstream integration: 2026-10-15

Baseline: `ae4a454f`. Integrated upstream endpoint: `e614de83`.
Backup: `codex/before-upstream-sync-2026-10-15-ae4a454f`.
No push, release publication, secrets access or Actions dispatch was performed.

## Commits and adaptation

Merge `b50fcb1a` preserves the five original upstream commits:

- `d011aa3e`: move Wayland portal waits off Tokio workers; use nonblocking state
  checks and serialize background portal-session closure.
- `b1761ee6`: run all VM Dart tests and add platform Rust/clipboard/DRM checks.
- `256dc9bc`: clarify platform-gated test placement and CI coverage.
- `e910029f`: use the configured proxy for WebSocket connections, preserving
  relay targets independently of the proxy's address family.
- `e614de83`: add the Unicode EXE-path regression. The fork already used
  ASCII-preserving lowercase offsets and checked slicing, so that implementation
  was kept instead of replaced by the upstream implementation.

The fork retains interactive cursor/key-state tests that upstream removed.
Keep their existing Linux exclusions and add the same exclusions to the new
Windows/macOS root-library test commands. The tests themselves are not deleted.
A new CI contract failed before this adaptation and passed after it.

`hbb_common` advances from `229b904508364c8997aad0fb5af57effac859f60` to
`5d52530b636fb296a324260b074780cf559e0093`. The exact 12-commit range includes
WebSocket/HTTP(S)/SOCKS proxy transport fixes, IPv6 authority handling, initial
TCP-stream reuse, read progress while flushing, direct WebSocket local-address
reporting, standalone WebRTC patch metadata and an additive USB permission enum.
It does not add USB forwarding to this client. No local submodule modifications
or unpublished submodule commits are required.

## Separate security remediation

Fresh RustSec database `edb58f5` reported four newly published advisories against
the existing rustls 0.23.45: RUSTSEC-2026-0346 through RUSTSEC-2026-0349.
Separate commit `45e4933c` updates only the locked rustls package/checksum to
0.23.46. No TLS-policy changes, manifest changes or unrelated dependency updates.
The quinn-proto 0.11.18 fix remains intact.

## Verification actually performed

- CI contract tests: 8 passed; includes RED/GREEN for interactive-test exclusions.
- Windows 7 compatibility-checker tests: 7 passed (not a real Windows 7 run).
- Actionlint passed; external shellcheck and pyflakes were disabled.
- Rustfmt 1.88 checks passed for all 7 changed Rust files outside the submodule.
- The updated hbb_common compiled on Windows with Rust 1.88. Both actual
  `src/custom_server.rs` tests passed in an ignored isolated Cargo harness.
- With rustls 0.23.46, the actual hbb_common WebSocket-proxy integration suite
  passed (one aggregate test with multiple transport cases).
- All 6 matching hbb_common proxy library tests passed, including Native TLS
  bidirectional transfer and read progress while a flush is blocked.
- `proxy_transport`: 6 of 7 tests passed, both before and after the rustls update.
  `https_reconnects_for_tls_fallback` fails on this Windows host at line 139:
  the test expects the server-side TLS accept to fail, but it succeeds. The
  client-side error-type assertion preceding the server-task join passes.
  Serial execution reproduces the failure, so parallel test interference is
  not required. This does not establish a production certificate bypass; it
  also does not prove every TLS fallback scenario correct. The test is retained
  unchanged in the upstream submodule, and is explicitly NOT counted as passed.
- Fresh Cargo audit after remediation: zero vulnerabilities, 24 existing
  warnings (21 unmaintained, 3 unsound). No advisory suppressions were added.
- Locked/offline manifest metadata passed for Windows x64, Windows 7 x64,
  Linux x64 and Android arm64. This is not cross-compilation.
- Existing signing/unsigned platform workflows, Windows 7 settings and the
  atomic AltGr matcher fix are unchanged. The fork's CI command retains its
  `--lib --bins` scope and interactive-test exclusions.

## Regression surface and remaining limits

Every existing runtime path changed is required by the approved integration:

- `src/server/wayland.rs`: initialization, display reads and portal-session
  closure must stop parking Tokio workers while a portal waits for the user.
- `libs/scrap/src/wayland/pipewire.rs`: session-hold queries become nonblocking.
- `src/ipc.rs`: the Linux portal-clear operation waits on a blocking worker.
- `src/server/connection.rs`: a thin Linux remote/camera disconnect hook calls
  the portal-specific background closer; other disconnect paths are unchanged.
- `src/client.rs`, `src/server.rs`: preserve relay destinations when connecting
  through a configured WebSocket proxy. Native network behavior changes here.
- `libs/hbb_common`: shared proxy/WebSocket transports and their ABI change as
  described above; no application authentication/signature policy is changed.
- `Cargo.lock`: the rustls patch release affects TLS users of that dependency.
- `.github/workflows/flutter-build.yml`: broader non-publishing test coverage;
  fork release permissions/signing remain unchanged.
- `.github/scripts/test_ci_contract.py`: test-only guard for necessary retained
  interactive-test exclusions. `src/custom_server.rs`: test-only addition.
- `AGENTS.md`: upstream test guidance only; no runtime behavior.

Full RustDesk native builds, new macOS/Windows library-test jobs, live Wayland
picker/multiple-session behavior, real configured proxies, Windows 7 devices,
Android devices and signed installation remain unverified. Dart production code
is unchanged; the earlier 199-test result was not rerun or claimed as a new run.
Bridge generation was not run. The known upstream TLS integration-test failure
must not be hidden by a statement that all tests pass.

Upload with `git push origin master`, then check the fork's platform builds and
CI. No force push is needed.
