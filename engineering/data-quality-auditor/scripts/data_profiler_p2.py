# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_profiler_base import *  # noqa: F403,E402
# fmt: off
from data_profiler_p1 import compute_dqs, dqs_label, load_csv, profile_column  # noqa: E402,E501
# fmt: on


def print_report(headers: list[str], profiles: list[dict], dqs: dict, total_rows: int, monitor: bool):
    print("=" * 64)
    print("DATA QUALITY AUDIT REPORT")
    print("=" * 64)
    print(f"Rows: {total_rows}  |  Columns: {len(headers)}")
    score = dqs["score"]
    indicator = "🟢" if score >= 85 else ("🟡" if score >= 65 else "🔴")
    print(f"\nData Quality Score (DQS): {score}/100  {indicator}")
    print(f"Verdict: {dqs_label(score)}")

    dims = dqs["dimensions"]
    print("\nDimension Breakdown:")
    for dim, val in dims.items():
        bar = int(val / 5)
        print(f"  {dim.capitalize():<14} {val:>5.1f}  {'█' * bar}{'░' * (20 - bar)}")

    print("\n" + "-" * 64)
    print("COLUMN PROFILES")
    print("-" * 64)

    issues = []
    for p in profiles:
        status = "🟢"
        col_issues = []
        if p["null_pct"] > 30:
            status = "🔴"
            col_issues.append(f"{p['null_pct']}% nulls — investigate root cause")
        elif p["null_pct"] > 10:
            status = "🟡"
            col_issues.append(f"{p['null_pct']}% nulls — impute cautiously")
        elif p["null_pct"] > 1:
            col_issues.append(f"{p['null_pct']}% nulls — impute with indicator")
        if p["is_constant"]:
            status = "🟡"
            col_issues.append("Constant column — zero variance, likely useless")
        if p["is_high_cardinality"] and p["inferred_type"] == "string":
            col_issues.append("High-cardinality string — check if categorical or free-text")

        print(f"\n  {status} {p['column']}")
        print(f"     Type: {p['inferred_type']}  |  Nulls: {p['null_count']} ({p['null_pct']}%)  |  Unique: {p['unique_count']}")
        if "min" in p:
            print(f"     Min: {p['min']}  Max: {p['max']}  Mean: {p['mean']}  Std: {p['std']}")
        if p["top_values"]:
            top = ", ".join(f"{v}({c})" for v, c in p["top_values"][:3])
            print(f"     Top values: {top}")
        for issue in col_issues:
            issues.append((p["column"], issue))
            print(f"     ⚠  {issue}")

    if issues:
        print("\n" + "-" * 64)
        print(f"ISSUES SUMMARY ({len(issues)} found)")
        print("-" * 64)
        for col, msg in issues:
            print(f"  [{col}] {msg}")

    if monitor:
        print("\n" + "-" * 64)
        print("MONITORING THRESHOLDS (copy into alerting config)")
        print("-" * 64)
        for p in profiles:
            if p["null_pct"] > 0:
                print(f"  {p['column']}: null_pct <= {min(p['null_pct'] * 1.5, 100):.1f}%")
            if "mean" in p and p["mean"] is not None:
                drift = abs(p.get("std", 0) or 0) * 2
                print(f"  {p['column']}: mean within [{p['mean'] - drift:.2f}, {p['mean'] + drift:.2f}]")

    print("\n" + "=" * 64)
def main():
    parser = argparse.ArgumentParser(description="Profile a CSV dataset and compute a Data Quality Score.")
    parser.add_argument("--file", required=True, help="Path to CSV file")
    parser.add_argument("--columns", help="Comma-separated list of columns to profile (default: all)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--monitor", action="store_true", help="Print monitoring thresholds")
    args = parser.parse_args()

    try:
        headers, rows = load_csv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("Error: CSV file is empty or has no data rows.", file=sys.stderr)
        sys.exit(1)

    selected = args.columns.split(",") if args.columns else headers
    missing_cols = [c for c in selected if c not in headers]
    if missing_cols:
        print(f"Error: columns not found: {', '.join(missing_cols)}", file=sys.stderr)
        sys.exit(1)

    profiles = [profile_column(col, [row.get(col, "") for row in rows]) for col in selected]
    dqs = compute_dqs(profiles, len(rows))

    if args.format == "json":
        print(json.dumps({"total_rows": len(rows), "dqs": dqs, "columns": profiles}, indent=2))
    else:
        print_report(selected, profiles, dqs, len(rows), args.monitor)
