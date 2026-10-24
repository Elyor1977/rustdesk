# Local DTLS security patch

Imported from `rustdesk-org/webrtc`, commit
`49c89bd8d30e6e62e4c1a96cee38fdc11f79ef63`, directory `dtls`, version 0.12.0.
The original MIT and Apache-2.0 licenses are retained.

The root workspace overrides only this Git dependency. Other WebRTC packages
remain pinned to their existing fork revision. The relative `webrtc-util` path is
replaced by a registry requirement; the root
`[patch.crates-io]` still selects the original fork's `webrtc-util`.

Only the library, its original unit tests, documentation and licenses are
vendored. Upstream example applications and their hub/clap dev dependencies
are omitted, avoiding unrelated example packages and public fixture keys.

Security migration: p256/p384 0.14, sec1 0.8 and their patched crypto-bigint
0.7.7 dependency. The new fallible key-generation API uses getrandom's SysRng;
uncompressed SEC1 wire format and borrowed/reusable secret semantics remain.
X25519 and DTLS state machines are unchanged.

Run actual crate tests from the repository root with
`cargo test --locked -p webrtc-dtls --lib`.
