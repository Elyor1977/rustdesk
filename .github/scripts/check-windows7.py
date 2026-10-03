#!/usr/bin/env python3
"""Reject known Windows 8+ loader dependencies in a Windows 7 x64 package."""

import argparse
from pathlib import Path

import pefile


UNSUPPORTED_DLLS = {
    "api-ms-win-core-path-l1-1-0.dll",
    "api-ms-win-core-synch-l1-2-0.dll",
    "api-ms-win-core-winrt-l1-1-0.dll",
    "api-ms-win-core-winrt-error-l1-1-0.dll",
    "bcryptprimitives.dll",
    "combase.dll",
    "d3d12.dll",
    "dxcore.dll",
    "shcore.dll",
}
UNSUPPORTED_APIS = {
    "CoIncrementMTAUsage",
    "CreateDXGIFactory2",
    "D3D12CreateDevice",
    "GetCurrentThreadStackLimits",
    "GetDpiForMonitor",
    "GetDpiForWindow",
    "GetOverlappedResultEx",
    "GetSystemTimePreciseAsFileTime",
    "GetTempPath2A",
    "GetTempPath2W",
    "ProcessPrng",
    "RoGetActivationFactory",
    "RoGetAgileReference",
    "RoInitialize",
    "RoOriginateErrorW",
    "SetProcessDpiAwareness",
    "SetProcessDpiAwarenessContext",
    "SetThreadDescription",
    "SetThreadDpiAwarenessContext",
    "WaitOnAddress",
    "WakeByAddressAll",
    "WakeByAddressSingle",
}


def compatibility_errors(pe):
    errors = []
    if pe.FILE_HEADER.Machine != 0x8664:
        errors.append("expected an x64 binary")
    header = pe.OPTIONAL_HEADER
    for label, major, minor in (
        ("OS", header.MajorOperatingSystemVersion, header.MinorOperatingSystemVersion),
        ("subsystem", header.MajorSubsystemVersion, header.MinorSubsystemVersion),
    ):
        if (major, minor) > (6, 1):
            errors.append(f"{label} version {major}.{minor} requires a newer Windows")
    for directory in ("DIRECTORY_ENTRY_IMPORT", "DIRECTORY_ENTRY_DELAY_IMPORT"):
        for entry in getattr(pe, directory, []):
            dll = entry.dll.decode("ascii", errors="replace")
            if dll.lower() in UNSUPPORTED_DLLS:
                errors.append(f"unsupported DLL: {dll}")
            for imported in entry.imports:
                if imported.name is None:
                    continue
                name = imported.name.decode("ascii", errors="replace")
                if name.rsplit(".", 1)[-1] in UNSUPPORTED_APIS:
                    errors.append(f"unsupported API: {dll}!{name}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    files = ([args.path] if args.path.is_file() else
             sorted(p for p in args.path.rglob("*")
                    if p.is_file() and p.suffix.lower() in {".exe", ".dll"}))
    if not files:
        parser.error(f"no EXE/DLL files found in {args.path}")
    failed = False
    for path in files:
        try:
            pe = pefile.PE(str(path))
            try:
                errors = compatibility_errors(pe)
            finally:
                pe.close()
        except (OSError, pefile.PEFormatError) as error:
            errors = [f"cannot inspect PE file: {error}"]
        for error in errors:
            print(f"{path}: {error}")
        failed |= bool(errors)
    if not failed:
        print(f"Checked {len(files)} Windows 7 x64 binaries; no known loader blockers found")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
