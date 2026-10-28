# zstd compatibility re-export

This package contains no compression implementation: `src/lib.rs` re-exports
the official, exact-pinned `zstd = 0.14.3`, which uses `zstd-safe 8.2.0` and
`zstd-sys 2.1.2+zstd.1.5.7` in the workspace lockfile.

The local version `0.13.1+rustdesk.1` identifies the compatibility requirement
of the existing root package and the unmodified upstream `hbb_common` submodule.
It is not a vendored copy of either the 0.13.1 or 0.13.3 implementation.
Using 0.13.3 here would incorrectly label this pure re-export as containing
the vulnerable `with_context` implementation introduced in 0.13.2
(RUSTSEC-2026-0391). No zstd advisory is suppressed.

All 0.13.1 feature flags are forwarded. The selected code paths (bulk and
stream decoding, transfer compression, HTTP decoding) are checked with the
workspace consumers, not claimed to be a universal API compatibility shim.
`compression-codecs 0.4.46` uses the same fixed v8 safe bindings directly.

The corrupt legacy-frame regression first failed against registry zstd 0.13.1
with zstd-safe 7.1.0 (reported output position 1024 instead of 0), and passes
against the re-export. It follows the six-byte input from the official fix:
https://github.com/gyscos/zstd-rs/commit/006e1d1ad1eeaf6b5d4c28329e70217adabcec43

Run `cargo test --locked -p zstd@0.13.1 --lib`. The package also participates
in Linux CI's existing workspace tests. Remove this adapter when upstream
`hbb_common` and the root manifest both require the fixed zstd release directly.
