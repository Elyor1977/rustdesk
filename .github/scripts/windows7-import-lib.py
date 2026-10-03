"""Locate the legacy windows-rs import library skipped by the Win7 target."""

import argparse
from pathlib import Path


def find_import_library(cargo_home):
    libraries = list((cargo_home / "registry" / "src").glob(
        "*/windows_x86_64_msvc-0.42.2/lib/windows.lib"))
    if len(libraries) != 1 or not libraries[0].is_file():
        raise FileNotFoundError("Expected one windows_x86_64_msvc 0.42.2 import library; run cargo fetch first")
    return libraries[0].parent.resolve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cargo_home", type=Path)
    args = parser.parse_args()
    try:
        print(find_import_library(args.cargo_home))
    except FileNotFoundError as error:
        parser.exit(1, f"{error}\n")
