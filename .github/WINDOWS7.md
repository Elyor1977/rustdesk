# Windows 7 SP1 x64 builds

The normal Windows artifacts target Windows 10 and newer. Windows 7 has a
separate manually triggered build so changing legacy dependencies does not
change the normal releases.

## Build and download

1. Push the Windows 7 changes to your fork.
2. Open **Actions → Windows 7 unsigned → Run workflow → master → Run workflow**.
3. When it succeeds, open the run and download
   `rustdesk-windows7-x86_64-unsigned-installers` under **Artifacts**.
4. Extract the archive. Use `rustdesk-1.5.0-windows7-x86_64.exe` or the matching
   `.msi` on Windows 7 SP1 x64.

For a signed build, use **Actions → Windows signed → Run workflow**, enable
**Build for Windows 7 SP1 x64**, and approve the `release` environment. It uses
the existing Windows certificate secrets and produces
`rustdesk-windows7-x86_64-installers`. A `v*` tag still publishes the normal
Windows/Android release; it does not automatically start a legacy build.

## Compatibility choices

- Rust uses pinned `nightly-2025-06-25` and the upstream target
  `x86_64-win7-windows-msvc`. Both the application library and the portable
  launcher rebuild `std` with `-Z build-std=std,panic_abort` and a static CRT.
  There is no downgrade of the application's Rust dependencies.
  Win7-only `windows_slim_errors` removes newer WinRT extended-error imports
  from `windows-result`; HRESULT error codes remain available.
  The old capture build helper maps the Win7 triple to its known x64 MSVC
  entry solely for its pointer-width check.
  Older windows-rs bindings also use an unversioned `windows.lib`; their
  target tables predate Win7. The Win7 job fetches the locked PC-target
  dependencies and adds the 0.42.2 and 0.48.5 import-library directories to the Win7 Rust
  linker search paths, preserving static CRT and slim-error flags, without
  changing dependencies or modifying Cargo's source cache.
  RustDesk's own C++ library uses a distinct name on Win7 to avoid shadowing
  the legacy `windows.lib` import library.
- Flutter stays at 3.24.5 and uses the existing SHA-256-checked RustDesk engine.
  The runner/plugins and vcpkg libraries are compiled with a Windows 7 baseline.
- Import checks cover the application EXE/DLL files, portable EXE, and MSI
  custom action DLL. Known Windows 8+ APIs, including `WakeByAddressSingle`,
  `WaitOnAddress`, and `ProcessPrng`, block publication of the build artifacts.
- Privacy Mode 2/IDD virtual displays and the bundled printer driver require
  newer Windows. Their drivers and helper DLLs are omitted from the Win7
  package. Existing OS capability checks remain responsible for availability.
- WinRT toast notifications require Windows 8+. The Win7 target excludes
  the notification dependency and logs installation/update results instead.
  The installation/update operations themselves are unchanged.
- The Rust DLL import check runs before Flutter packaging; the complete
  application, portable launcher, and MSI custom action checks still run.
  Failed Win7 runs retain available binaries for seven days in the
  `windows7-failed-build-diagnostics` artifact; these are not release installers.

## Validation limits

A successful build/import check is not a Windows 7 runtime test. Validate on
an updated Windows 7 SP1 x64 computer: startup, EXE/MSI installation, service,
incoming/outgoing connections, capture, keyboard/mouse, clipboard, file
transfer, sound, reconnect, and uninstall. GPU encoding/decoding depends on
the installed GPU driver. The import check rejects known loader blockers;
it is not an exhaustive inventory of all APIs exported by Windows 7.

Upstream references:
[Rust Win7 target](https://doc.rust-lang.org/rustc/platform-support/win7-windows-msvc.html),
[Cargo build-std](https://doc.rust-lang.org/cargo/reference/unstable.html#build-std).

## Existing paths changed

- `.cargo/config.toml`: new target-specific static CRT and error-reporting flags.
- `.github/workflows/windows-x64.yml`: optional Win7 toolchain, native baseline,
  Rust/portable rebuild, import checks, and distinct artifact names.
- `.github/workflows/windows-signed.yml`: manual Win7 selector passed through
  the existing approval/signing flow.
- `flutter/windows/CMakeLists.txt`: Win7-only compiler definitions and minimum
  subsystem version for the runner and plugins.
- `libs/scrap/build.rs`: Win7-only target mapping for the legacy build helper.
- `build.rs`: Win7-only C++ library name avoids a collision with windows-rs.
- `Cargo.toml` and `src/core_main.rs`: exclude WinRT toast notifications on
  Win7; ordinary Windows notification behavior stays unchanged.
- `libs/portable/generate.py`: opt-in metadata-only mode allows a separate
  `build-std` invocation for the launcher; its default build path is unchanged.
