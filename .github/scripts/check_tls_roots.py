"""Fail closed before exempting the audited webpki-roots 0.26.11 re-export."""
from pathlib import Path
import re
import tomllib


REGISTRY = "registry+https://github.com/rust-lang/crates.io-index"
WRAPPER_CHECKSUM = "521bc38abb08001b01866da9f51eb7c5d647a19260e00054a8c7fd5f9e57f7a9"


def check_roots(packages):
    roots = [p for p in packages if p["name"] == "webpki-roots"]
    fixed = {p["version"] for p in roots
             if p.get("source") == REGISTRY
             and re.fullmatch(r"1\.\d+\.\d+", p["version"])
             and tuple(map(int, p["version"].split("."))) >= (1, 0, 10)}
    for package in roots:
        if package.get("source") == REGISTRY and package["version"] in fixed:
            continue
        # Published 0.26.11 contains only `pub use parent::TLS_SERVER_ROOTS`.
        # Its verified crate must resolve exclusively to a patched v1 package.
        if (package["version"] == "0.26.11"
                and package.get("source") == REGISTRY
                and package.get("checksum") == WRAPPER_CHECKSUM
                and package.get("dependencies") in
                [[f"webpki-roots {version}"] for version in fixed]):
            continue
        raise ValueError(f"Unaudited TLS roots package: {package['version']}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    check_roots(tomllib.loads((root / "Cargo.lock").read_text(encoding="utf-8"))["package"])
    print("TLS root versions verified")
