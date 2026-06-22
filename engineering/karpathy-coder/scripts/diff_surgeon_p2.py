# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from diff_surgeon_base import *  # noqa: F403,E402
# fmt: off
from diff_surgeon_p1 import analyze_file_diff, get_diff, parse_hunks  # noqa: E402,E501
# fmt: on


def main():
    p = argparse.ArgumentParser(
        description="Detect diff noise — changes that don't trace to the stated goal (Karpathy Principle #3).",
        epilog="Run before committing to catch drive-by refactors and style drift.",
    )
    p.add_argument("--diff", default=None, help="Git diff range (e.g. HEAD~1..HEAD). Default: staged changes.")
    p.add_argument("--file", default=None, help="Read diff from a file instead of git")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    diff_text = get_diff(args)
    if not diff_text.strip():
        result = {"status": "ok", "message": "No diff to analyze", "files": 0, "noise_lines": 0, "verdict": "CLEAN"}
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("No diff to analyze. Stage changes first (git add) or specify --diff range.")
        return

    file_diffs = parse_hunks(diff_text)
    all_findings = []
    file_results = []

    for fd in file_diffs:
        findings = analyze_file_diff(fd)
        if findings:
            file_results.append({"file": fd["file"], "findings": findings})
            all_findings.extend(findings)

    total_noise = len(all_findings)
    total_changes = sum(
        len([l for l in fd["lines"] if l["type"] == "change"]) for fd in file_diffs
    )
    noise_ratio = total_noise / total_changes if total_changes > 0 else 0

    verdict = "CLEAN" if noise_ratio < 0.1 else ("NOISY" if noise_ratio < 0.3 else "VERY_NOISY")

    result = {
        "status": "ok",
        "files_in_diff": len(file_diffs),
        "total_change_lines": total_changes,
        "noise_lines": total_noise,
        "noise_ratio": round(noise_ratio, 2),
        "verdict": verdict,
        "file_results": file_results,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Diff Surgeon — {len(file_diffs)} files, {total_changes} changed lines")
    print(f"Noise ratio: {noise_ratio:.0%} ({total_noise} noise lines)")
    print(f"Verdict: {verdict}")
    if file_results:
        print()
        for fr in file_results:
            print(f"  {fr['file']}:")
            categories = {}
            for f in fr["findings"]:
                categories.setdefault(f["category"], []).append(f["line"])
            for cat, lines in categories.items():
                print(f"    [{cat}] {len(lines)} instance(s)")
                for l in lines[:3]:
                    print(f"      {l}")
                if len(lines) > 3:
                    print(f"      ... and {len(lines) - 3} more")
        print()
        print("Recommendation: review flagged lines. Remove changes that don't trace to your task.")
    else:
        print("\n  All changes look intentional. Clean diff.")

    sys.exit(1 if verdict != "CLEAN" else 0)
