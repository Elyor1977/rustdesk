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

## crypto-bigint: unresolved release blocker

The audit still reports RUSTSEC-2026-0387 for crypto-bigint 0.5.5. No new ignore
was added. The dependency comes through the pinned WebRTC DTLS implementation,
p256/p384 0.13 and elliptic-curve 0.13.8. Adding crypto-bigint 0.7.6 alongside it
would not remove the vulnerable copy.

The existing WebRTC fork has required networking patches. Its current master
is a different, substantially diverged architecture, not a compatible security
upgrade. The alternative is a separately maintained DTLS patch: migrate its
p256/p384 APIs and RNG integration, retain licenses/provenance, and run the real
DTLS handshake/interoperability tests. Vendoring the current DTLS source alone
would introduce 91 Rust files (approximately 543 KB), before the actual fix.
That scope expansion needs maintainer approval; no cryptographic implementation
or network stack was silently replaced. Review again before the next release.

The release remains blocked by the crypto-bigint audit finding. Pre-existing
unsound warnings for atty, glib and users also remain. Nothing was pushed or
released.
