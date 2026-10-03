"""Locate legacy windows-rs import libraries skipped by the Win7 target."""

import argparse
from pathlib import Path


def find_import_libraries(cargo_home):
    directories = []
    for version, filename in (("0.42.2", "windows.lib"), ("0.48.5", "windows.0.48.5.lib")):
        libraries = list((cargo_home / "registry" / "src").glob(
            f"*/windows_x86_64_msvc-{version}/lib/{filename}"))
        if len(libraries) != 1 or not libraries[0].is_file():
            raise FileNotFoundError(f"Expected one {filename} import library; run cargo fetch first")
        directories.append(libraries[0].parent.resolve())
    return directories


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cargo_home", type=Path)
    args = parser.parse_args()
    try:
        print("\n".join(str(path) for path in find_import_libraries(args.cargo_home)))
    except FileNotFoundError as error:
        parser.exit(1, f"{error}\n")
