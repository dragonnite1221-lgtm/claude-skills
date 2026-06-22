# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from outlier_detector_base import *  # noqa: F403,E402
# fmt: off
from outlier_detector_p1 import analyze_column, is_null, load_csv, to_float  # noqa: E402,E501
# fmt: on


def print_report(results: list[dict]):
    print("=" * 64)
    print("OUTLIER DETECTION REPORT")
    print("=" * 64)

    clean = [r for r in results if r.get("outlier_count", 0) == 0 and "status" not in r]
    flagged = [r for r in results if r.get("outlier_count", 0) > 0]
    skipped = [r for r in results if "status" in r]

    print(f"\nColumns analyzed: {len(results) - len(skipped)}")
    print(f"Clean:   {len(clean)}")
    print(f"Flagged: {len(flagged)}")
    if skipped:
        print(f"Skipped: {len(skipped)} ({', '.join(r['column'] for r in skipped)})")

    if flagged:
        print("\n" + "-" * 64)
        print("FLAGGED COLUMNS")
        print("-" * 64)
        for r in sorted(flagged, key=lambda x: -x.get("outlier_pct", 0)):
            pct = r.get("outlier_pct", 0)
            indicator = "🔴" if pct > 5 else "🟡"
            print(f"\n  {indicator} {r['column']} ({r['method']})")
            print(f"     Outliers: {r['outlier_count']} / {r['total_numeric']} rows ({pct}%)")
            if "lower_bound" in r:
                print(f"     Bounds: [{r['lower_bound']}, {r['upper_bound']}]  |  IQR: {r['iqr']}")
            if "mean" in r:
                print(f"     Mean: {r['mean']}  |  Std: {r['std']}  |  Threshold: ±{r['threshold']}σ")
            if "median" in r:
                print(f"     Median: {r['median']}  |  MAD: {r['mad']}  |  Threshold: {r['threshold']}")
            if r.get("outlier_values"):
                vals = ", ".join(str(v) for v in r["outlier_values"][:8])
                print(f"     Sample outlier values: {vals}")
            print(f"     Assessment: {r['risk_assessment']}")

    if clean:
        cols = ", ".join(r["column"] for r in clean)
        print(f"\n🟢 Clean columns: {cols}")

    print("\n" + "=" * 64)
def main():
    parser = argparse.ArgumentParser(description="Detect outliers in numeric columns of a CSV dataset.")
    parser.add_argument("--file", required=True, help="Path to CSV file")
    parser.add_argument("--method", choices=["iqr", "zscore", "mzscore"], default="iqr",
                        help="Detection method (default: iqr)")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Method threshold (IQR multiplier default 1.5; Z-score default 3.0; mzscore default 3.5)")
    parser.add_argument("--columns", help="Comma-separated columns to check (default: all numeric)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    # Set default thresholds per method
    if args.threshold is None:
        args.threshold = {"iqr": 1.5, "zscore": 3.0, "mzscore": 3.5}[args.method]

    try:
        headers, rows = load_csv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Error: CSV file is empty.", file=sys.stderr)
        sys.exit(1)

    selected = args.columns.split(",") if args.columns else headers
    missing_cols = [c for c in selected if c not in headers]
    if missing_cols:
        print(f"Error: columns not found: {', '.join(missing_cols)}", file=sys.stderr)
        sys.exit(1)

    results = []
    for col in selected:
        raw = [row.get(col, "") for row in rows]
        nums = [n for v in raw if not is_null(v) and (n := to_float(v)) is not None]
        results.append(analyze_column(col, nums, args.method, args.threshold))

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print_report(results)
