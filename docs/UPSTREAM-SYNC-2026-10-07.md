# Upstream integration: 2026-10-07

Fork baseline: `a375f8a1cd114817c3bbbb9a8bc9770757b679f6`.
Upstream endpoint: `f0bd880fe7f0e574a1a36811099ba97597429807`.
Local backup: `codex/before-upstream-sync-2026-10-07-a375f8a1`.

## Integrated commits

- `e8a86592`: fill Polish clipboard-permission and voice-call translations.
- `9f9585ce`: ignore server-pushed rendezvous lists in NAT replies and
  ConfigureUpdate messages.
- `a916af8f`: fill the Portuguese voice-call audio-capture prompt.
- `f0bd880f`: Dutch translation consistency and missing clipboard text.

Normal merge preserves all four upstream commits and fork history. No conflicts.
No new dependencies, configuration options, or production abstractions.

## Verification

- OCR delegation preview/rules and manual review: all five source files reviewed,
  none skipped; no blocking findings.
- Exact changed-file CI rustfmt command and actionlint passed.
- Five CI contract tests and seven Windows 7 checker tests passed.
- Flutter 3.24.5: analyze succeeded with 271 informational findings and no
  warnings/errors; all 136 tests passed.
- Flutter pub get resolved SDK-compatible test dependencies locally; its generated
  lockfile changes were discarded. Flutter results apply to this resolved test
  environment, not a frozen installation of the committed lockfile.
- All 780 translation keys per changed locale remain unchanged; existing
  placeholder and escape sequences are preserved.
- Source check detects both configuration-update paths before integration and
  their absence afterward. This is a static check, not a runtime regression test.
- CI, signing, Windows 7 settings, manifests, lockfiles, Flutter source, and
  submodule revisions remain identical to the fork baseline.

## Regression surface and remaining checks

- `src/common.rs`: NAT replies still supply ports for NAT classification, but
  no longer overwrite rendezvous addresses or configuration serial.
- `src/rendezvous_mediator.rs`: ConfigureUpdate falls through to the existing
  ignored-message branch and no longer overwrites addresses/serial or restarts
  the mediator. TCP and UDP share this handler. Other message branches are unchanged.
- `src/lang/nl.rs`, `src/lang/pl.rs`, `src/lang/pt_PT.rs`: display text only.

Automatic rendezvous-list migration pushed by a server is intentionally disabled.
Existing locally configured addresses are not cleared. Deployments relying on
server-pushed migration must manage addresses separately.

Native Rust tests were not compiled: the offline Cargo cache lacks the pinned
tungstenite Git dependency. No native build or live-server NAT/TCP/UDP test,
Android build, Windows 7 runtime test, or signing operation was performed.
GitHub workflows were not started; the agent did not push changes.
