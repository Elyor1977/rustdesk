# Security dependencies — 2026-10-24

## Tokio

Updated the minimum root dev dependency and the authoritative lockfile from Tokio
1.44.2 to 1.51.6 (LTS). This is a patched version for
[RUSTSEC-2026-0386](https://rustsec.org/advisories/RUSTSEC-2026-0386.html).
Cargo resolved the required mio, socket2, tokio-macros and platform dependencies;
the lockfile was not hand-edited. Rust 1.88 compiled the updated dependency graph.

Regression surface: `Cargo.toml` and `Cargo.lock` only. The shared Tokio runtime,
network I/O, timers, synchronization and filesystem adapters use the new version.
No application interfaces, WebRTC patches, submodules, CI/signing policies or
audit exemptions were changed.

Verification: `cargo test --locked -p base --lib` passed (26 tests, 3 existing
ignored); `cargo test --locked -p hbb_common --lib` passed (104 tests, none
ignored); all 20 `.github/scripts` tests and the TLS roots guard passed;
`git diff --check` passed. Logs: `target/integration-tools/security-2026-10-24-*`.
The updated lockfile audit no longer reports RUSTSEC-2026-0386. Full application
builds and Windows 7 device execution are not established by these checks.

## crypto-bigint: security migration completed locally

After explicit approval, vendored only webrtc-dtls 0.12.0 from the exact existing
fork revision into `libs/webrtc-dtls`. Licenses and provenance are retained in
that directory. Examples, their public fixture keys, and unused hub/clap example
dependencies are omitted. All 91 original Rust source/test files are retained;
only `curve/named_curve.rs`, `prf/mod.rs` and `prf/prf_test.rs` have functional
changes; one trailing space in the imported `conn/conn_test.rs` was removed to
pass the added-file whitespace check.

The Git patch overrides only DTLS. The rest of WebRTC, including the fork's
IPv6 and SCTP changes, remains pinned to 49c89bd8. DTLS now uses p256/p384 0.14
and sec1 0.8; Cargo resolves crypto-bigint 0.7.7 and removes 0.5.5 entirely.
The new fallible generation API uses OS randomness through getrandom SysRng,
preserving uncompressed SEC1 points, shared-secret bytes and reusable borrowed
ephemeral secrets. X25519, certificate validation and handshake state machines
are not rewritten. getrandom 0.4.3 explicitly selects its legacy Windows backend
for `target_vendor = "win7"`; this is source verification, not a Win7 device test.

### Verification

- Before migration: the original 60 DTLS tests passed; audit reported
  RUSTSEC-2026-0387 for crypto-bigint 0.5.5.
- Final DTLS suite with all features: 63 passed in debug and 63 passed in release,
  none ignored. The two added
  tests compare P256/P384 ECDH against independent ring peers, check wire/secret
  lengths and repeat derivation, and reject malformed peer points.
- Mutation check: changing P256 output to compressed points made the new
  interoperability test fail (33 bytes instead of 65); restored before final tests.
- Actual hbb_common with `--features webrtc`: 135 passed, none ignored, including
  WebRTC loopback, teardown, framing and buffered-transfer tests.
- Base file-transfer regression suite: 26 passed, 3 previously ignored.
- All 20 CI/TLS/Win7 script tests, TLS roots guard, actionlint (without
  ShellCheck/Pyflakes), and rustfmt 1.88 over all 91 vendored files passed.
- Both normal audit and the current CI audit command report zero vulnerability
  findings using the current local RustSec database. No audit exemptions added.
  The 24 unmaintained and 3 unsound warnings (atty, glib, users) remain; this is
  not a claim that the entire dependency graph is free of security debt.

Logs are under `target/integration-tools/dtls-2026-10-24-*` (ignored).
Linux CI's workspace run now includes DTLS; Windows/macOS full Flutter CI gets
an explicit DTLS test command. No other build/signing policies changed.

### Regression surface and limits

Existing files changed: `Cargo.toml` selects the local DTLS crate and makes it
a workspace member for real tests; `Cargo.lock` records only the required crypto
chain and test dependencies; `flutter-build.yml` adds the missing package tests.
The existing production path affected is WebRTC DTLS P256/P384 key exchange.
No application interface, submodule, TCP/KCP implementation or UI is changed.

The earlier sync report's crypto-bigint release blocker is superseded by these
results. Full Windows/Android/Linux application builds, real peer/device
interoperability and Win7 execution still require the normal CI/device gates.
P384 has independent ECDH interoperability coverage, not a forced full P384
handshake: the existing handshake API has no curve preference option. Nothing
was pushed or released.
