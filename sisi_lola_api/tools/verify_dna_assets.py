"""Utility script to confirm DNA reference images exist on disk."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.config import SisiLolaDNA  # noqa: E402


def main() -> None:
    root_dir = ROOT_DIR
    missing: list[str] = []

    print("==> Verifying DNA reference assets")
    for relative_path in SisiLolaDNA.DNA_IMAGE_PATHS:
        asset_path = root_dir / relative_path
        if asset_path.exists():
            print(f"✅ {relative_path} -> {asset_path}")
        else:
            print(f"❌ {relative_path} MISSING (expected at {asset_path})")
            missing.append(relative_path)

    if missing:
        print("\n⚠️  Missing assets detected. Re-export the images listed above before running tests.")
    else:
        print("\nAll DNA reference images are present.")


if __name__ == "__main__":
    main()
