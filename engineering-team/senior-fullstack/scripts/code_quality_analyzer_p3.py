# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_analyzer_base import *  # noqa: F403,E402
# fmt: off
from code_quality_analyzer_p1 import ALL_CODE_EXTENSIONS, should_skip  # noqa: E402,E501
# fmt: on


def analyze_test_coverage(project_path: Path) -> Dict:
    """Estimate test coverage based on file analysis."""
    test_files = []
    source_files = []

    for filepath in project_path.rglob("*"):
        if should_skip(filepath) or not filepath.is_file():
            continue

        if filepath.suffix in ALL_CODE_EXTENSIONS:
            name = filepath.stem.lower()
            if "test" in name or "spec" in name or "_test" in name:
                test_files.append(filepath)
            elif not name.startswith("_"):
                source_files.append(filepath)

    source_count = len(source_files)
    test_count = len(test_files)

    # Estimate coverage ratio
    if source_count == 0:
        ratio = 0
    else:
        ratio = min(100, int((test_count / source_count) * 100))

    return {
        "source_files": source_count,
        "test_files": test_count,
        "estimated_coverage": ratio,
        "rating": "good" if ratio >= 70 else "adequate" if ratio >= 40 else "poor",
        "recommendation": None if ratio >= 70 else f"Consider adding more tests ({70 - ratio}% gap to target)"
    }
def analyze_documentation(project_path: Path) -> Dict:
    """Analyze documentation quality."""
    docs = {
        "has_readme": False,
        "has_contributing": False,
        "has_license": False,
        "has_changelog": False,
        "api_docs": [],
        "score": 0
    }

    readme_patterns = ["README.md", "README.rst", "README.txt", "readme.md"]
    for pattern in readme_patterns:
        if (project_path / pattern).exists():
            docs["has_readme"] = True
            docs["score"] += 30
            break

    if (project_path / "CONTRIBUTING.md").exists():
        docs["has_contributing"] = True
        docs["score"] += 15

    license_patterns = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
    for pattern in license_patterns:
        if (project_path / pattern).exists():
            docs["has_license"] = True
            docs["score"] += 15
            break

    changelog_patterns = ["CHANGELOG.md", "HISTORY.md", "CHANGES.md"]
    for pattern in changelog_patterns:
        if (project_path / pattern).exists():
            docs["has_changelog"] = True
            docs["score"] += 10
            break

    # Check for API docs
    api_doc_dirs = ["docs", "documentation", "api-docs"]
    for doc_dir in api_doc_dirs:
        doc_path = project_path / doc_dir
        if doc_path.is_dir():
            docs["api_docs"].append(str(doc_path))
            docs["score"] += 30
            break

    return docs
