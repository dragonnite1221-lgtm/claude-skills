# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from complexity_checker_base import *  # noqa: F403,E402
# fmt: off
from complexity_checker_p1 import THRESHOLDS  # noqa: E402,E501
from complexity_checker_p2 import analyze_file, collect_files  # noqa: E402,E501
# fmt: on


def main():
    p = argparse.ArgumentParser(
        description="Detect over-engineering in Python/TypeScript files (Karpathy Principle #2).",
        epilog="Thresholds: strict (new code), medium (default), relaxed (legacy).",
    )
    p.add_argument("target", help="File or directory to analyze")
    p.add_argument(
        "--threshold",
        choices=sorted(THRESHOLDS.keys()),
        default="medium",
        help="Strictness level (default: medium)",
    )
    p.add_argument(
        "--ext",
        default="py,ts,tsx,js,jsx",
        help="Comma-separated file extensions to scan (default: py,ts,tsx,js,jsx)",
    )
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    thresholds = THRESHOLDS[args.threshold]
    extensions = [e.strip().lstrip(".") for e in args.ext.split(",")]
    files = collect_files(args.target, extensions)

    if not files:
        msg = f"No files found matching extensions: {extensions}"
        if args.json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"[error] {msg}", file=sys.stderr)
        sys.exit(1)

    results = []
    for f in sorted(files):
        r = analyze_file(f, thresholds)
        if r:
            results.append(r)

    total_findings = sum(len(r["findings"]) for r in results)
    avg_score = sum(r["score"] for r in results) / len(results) if results else 100

    summary = {
        "status": "ok",
        "threshold": args.threshold,
        "files_analyzed": len(results),
        "total_findings": total_findings,
        "average_score": round(avg_score, 1),
        "verdict": "PASS" if total_findings == 0 else ("WARN" if avg_score >= 50 else "FAIL"),
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    print(f"Karpathy Simplicity Check — {len(results)} files, threshold: {args.threshold}")
    print(f"Average score: {avg_score:.0f}/100  Findings: {total_findings}")
    print()
    for r in results:
        if not r["findings"]:
            continue
        print(f"  {r['file']}  (score {r['score']}/100)")
        for f in r["findings"]:
            line = f"  line {f['line']}" if "line" in f else ""
            print(f"    [{f['severity'].upper()}] {f['rule']}{line}: {f['message']}")
        print()
    if total_findings == 0:
        print("  No findings. Code looks appropriately simple.")
    print(f"\nVerdict: {summary['verdict']}")
