"""Drift guard: committed skill `.zip` packages must match their source folders.

Code review H2 found several committed `*.zip` snapshots (e.g. senior-backend,
app-store-optimization) had drifted from the live source folder, so users who
install from the zip get a stale, unverified copy. This test compares each
committed zip against its sibling source directory (file set + byte contents,
ignoring timestamps) and fails on any drift. Regenerate with
`scripts/regen_skill_zips.py` after editing a skill that ships a zip.
"""

import os
import subprocess
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _committed_zips() -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "*.zip"], cwd=REPO_ROOT, text=True
    )
    return [line for line in out.splitlines() if line.strip()]


ZIPS = _committed_zips()


@pytest.mark.skipif(not ZIPS, reason="no committed skill zips")
@pytest.mark.parametrize("zip_rel", ZIPS)
def test_zip_matches_source_folder(zip_rel: str) -> None:
    zip_path = REPO_ROOT / zip_rel
    base = Path(zip_rel).stem
    src_dir = zip_path.parent / base
    assert src_dir.is_dir(), f"{zip_rel}: no sibling source folder '{base}/'"

    # Only git-tracked source files are expected to ship — untracked
    # __pycache__/*.pyc and other local noise are not part of the package.
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", str(src_dir.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        text=True,
    ).split("\0")
    src_files = {
        str(Path(base) / (REPO_ROOT / t).relative_to(src_dir)): (
            REPO_ROOT / t
        ).read_bytes()
        for t in tracked
        if t
    }

    with zipfile.ZipFile(zip_path) as zf:
        zip_files = {
            name: zf.read(name)
            for name in zf.namelist()
            if not name.endswith("/")
        }

    missing = sorted(set(src_files) - set(zip_files))
    extra = sorted(set(zip_files) - set(src_files))
    assert not missing, f"{zip_rel}: source files missing from zip: {missing}"
    assert not extra, f"{zip_rel}: stale files in zip not in source: {extra}"

    drifted = sorted(k for k in src_files if src_files[k] != zip_files[k])
    assert not drifted, f"{zip_rel}: contents drifted from source: {drifted}"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([os.path.abspath(__file__), "-q"]))
