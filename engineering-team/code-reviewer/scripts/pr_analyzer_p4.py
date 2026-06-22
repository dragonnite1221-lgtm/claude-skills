# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pr_analyzer_base import *  # noqa: F403,E402
# fmt: off
from pr_analyzer_p3 import analyze_pr  # noqa: E402,E501
# fmt: on


def print_report(analysis: Dict) -> None:
    """Print human-readable analysis report."""
    if analysis["status"] == "no_changes":
        print("No changes detected.")
        return

    summary = analysis["summary"]
    risks = analysis["risks"]

    print("=" * 60)
    print("PR ANALYSIS REPORT")
    print("=" * 60)

    print(f"\nComplexity: {summary['complexity_score']}/10 ({summary['complexity_label']})")
    print(f"Files Changed: {summary['files_changed']}")
    print(f"Lines: +{summary['total_additions']} / -{summary['total_deletions']}")
    print(f"Commits: {summary['commits']}")

    # Risk summary
    print("\n--- RISK SUMMARY ---")
    print(f"Critical: {len(risks['critical'])}")
    print(f"High: {len(risks['high'])}")
    print(f"Medium: {len(risks['medium'])}")
    print(f"Low: {len(risks['low'])}")

    # Critical and high risks details
    if risks["critical"]:
        print("\n--- CRITICAL RISKS ---")
        for risk in risks["critical"]:
            print(f"  [{risk['file']}] {risk['message']} (x{risk['count']})")

    if risks["high"]:
        print("\n--- HIGH RISKS ---")
        for risk in risks["high"]:
            print(f"  [{risk['file']}] {risk['message']} (x{risk['count']})")

    # Commit message issues
    if analysis["commit_issues"]:
        print("\n--- COMMIT MESSAGE ISSUES ---")
        for issue in analysis["commit_issues"][:5]:
            print(f"  {issue['commit']}: {issue['issue']}")

    # Review order
    print("\n--- SUGGESTED REVIEW ORDER ---")
    for i, filepath in enumerate(analysis["review_order"], 1):
        file_info = next(f for f in analysis["files"] if f["path"] == filepath)
        print(f"  {i}. [{file_info['category'].upper()}] {filepath}")

    print("\n" + "=" * 60)
def main():
    parser = argparse.ArgumentParser(
        description="Analyze pull request for review complexity and risks"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    parser.add_argument(
        "--base", "-b",
        default="main",
        help="Base branch for comparison (default: main)"
    )
    parser.add_argument(
        "--head",
        default="HEAD",
        help="Head branch/commit for comparison (default: HEAD)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file"
    )

    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()

    if not (repo_path / ".git").exists():
        print(f"Error: {repo_path} is not a git repository", file=sys.stderr)
        sys.exit(1)

    analysis = analyze_pr(repo_path, args.base, args.head)

    if args.json:
        output = json.dumps(analysis, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)
    else:
        print_report(analysis)
