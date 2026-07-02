#!/usr/bin/env python3
"""Regenerate committed skill `.zip` packages from their source folders.

Each `<dir>/<name>.zip` is rebuilt from `<dir>/<name>/` deterministically
(sorted entries, fixed timestamp, no host metadata) so a re-run is a no-op when
nothing changed. Run this after editing a skill that ships a zip; the
`tests/test_skill_zip_integrity.py` guard fails if a zip drifts from source.

    python3 scripts/regen_skill_zips.py
"""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


def regenerate() -> int:
    zips = subprocess.check_output(
        ["git", "ls-files", "*.zip"], cwd=REPO_ROOT, text=True
    ).split()
    count = 0
    for rel in zips:
        zip_path = REPO_ROOT / rel
        base = zip_path.stem
        src_dir = zip_path.parent / base
        if not src_dir.is_dir():
            print(f"skip (no source folder): {rel}")
            continue
        files = sorted(p for p in src_dir.rglob("*") if p.is_file())
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                arc = str(Path(base) / f.relative_to(src_dir))
                info = zipfile.ZipInfo(arc, date_time=FIXED_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, f.read_bytes())
        count += 1
    print(f"regenerated {count} skill zips")
    return count


if __name__ == "__main__":
    regenerate()
