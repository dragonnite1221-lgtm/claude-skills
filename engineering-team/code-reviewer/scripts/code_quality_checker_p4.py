# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from code_quality_checker_base import *  # noqa: F403,E402
# fmt: off
from code_quality_checker_p1 import LANGUAGE_EXTENSIONS  # noqa: E402,E501
from code_quality_checker_p3 import analyze_file, get_grade  # noqa: E402,E501
# fmt: on


def analyze_directory(
    dir_path: Path,
    recursive: bool = True,
    language: Optional[str] = None
) -> Dict:
    """Analyze all files in a directory."""
    results = []
    extensions = []

    if language:
        extensions = LANGUAGE_EXTENSIONS.get(language, [])
    else:
        for exts in LANGUAGE_EXTENSIONS.values():
            extensions.extend(exts)

    pattern = "**/*" if recursive else "*"

    for ext in extensions:
        for filepath in dir_path.glob(f"{pattern}{ext}"):
            if "node_modules" in str(filepath) or ".git" in str(filepath):
                continue
            result = analyze_file(filepath)
            if "error" not in result:
                results.append(result)

    if not results:
        return {"error": "No supported files found"}

    total_score = sum(r["quality_score"] for r in results)
    avg_score = total_score / len(results)
    total_smells = sum(len(r["smells"]) for r in results)
    total_violations = sum(len(r["solid_violations"]) for r in results)

    return {
        "directory": str(dir_path),
        "files_analyzed": len(results),
        "average_score": round(avg_score, 1),
        "overall_grade": get_grade(int(avg_score)),
        "total_code_smells": total_smells,
        "total_solid_violations": total_violations,
        "files": sorted(results, key=lambda x: x["quality_score"])
    }
def print_report(analysis: Dict) -> None:
    """Print human-readable analysis report."""
    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return

    print("=" * 60)
    print("CODE QUALITY REPORT")
    print("=" * 60)

    if "file" in analysis:
        print(f"\nFile: {analysis['file']}")
        print(f"Language: {analysis['language']}")
        print(f"Quality Score: {analysis['quality_score']}/100 ({analysis['grade']})")

        metrics = analysis["metrics"]
        print(f"\nLines: {metrics['lines']['total']} ({metrics['lines']['code']} code, {metrics['lines']['comment']} comments)")
        print(f"Functions: {metrics['functions']}")
        print(f"Classes: {metrics['classes']}")
        print(f"Avg Complexity: {metrics['avg_complexity']}")

        if analysis["smells"]:
            print("\n--- CODE SMELLS ---")
            for smell in analysis["smells"][:10]:
                print(f"  [{smell['severity'].upper()}] {smell['message']} ({smell['location']})")

        if analysis["solid_violations"]:
            print("\n--- SOLID VIOLATIONS ---")
            for v in analysis["solid_violations"]:
                print(f"  [{v['principle']}] {v['message']}")
    else:
        print(f"\nDirectory: {analysis['directory']}")
        print(f"Files Analyzed: {analysis['files_analyzed']}")
        print(f"Average Score: {analysis['average_score']}/100 ({analysis['overall_grade']})")
        print(f"Total Code Smells: {analysis['total_code_smells']}")
        print(f"Total SOLID Violations: {analysis['total_solid_violations']}")

        print("\n--- FILES BY QUALITY ---")
        for f in analysis["files"][:10]:
            print(f"  {f['quality_score']:3d}/100 [{f['grade']}] {f['file']}")

    print("\n" + "=" * 60)
