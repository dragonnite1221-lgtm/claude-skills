# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from missing_value_analyzer_base import *  # noqa: F403,E402
# fmt: off
from missing_value_analyzer_p1 import classify_mechanism, compute_cooccurrence, compute_null_mask, infer_type, load_csv, null_stats, recommend_strategy  # noqa: E402,E501
# fmt: on


def print_report(headers: list[str], rows: list[dict], masks: dict, threshold: float):
    total = len(rows)
    print("=" * 64)
    print("MISSING VALUE ANALYSIS REPORT")
    print("=" * 64)
    print(f"Rows: {total}  |  Columns: {len(headers)}")

    results = []
    for col in headers:
        mask = masks[col]
        stats = null_stats(mask)
        if stats["pct"] / 100 < threshold and stats["count"] > 0:
            continue
        raw_vals = [row.get(col, "") for row in rows]
        col_type = infer_type(raw_vals)
        mechanism = classify_mechanism(col, mask, masks)
        strategy = recommend_strategy(stats["pct"], col_type)
        results.append({
            "column": col,
            "null_count": stats["count"],
            "null_pct": stats["pct"],
            "col_type": col_type,
            "mechanism": mechanism,
            "strategy": strategy,
        })

    fully_complete = [col for col in headers if null_stats(masks[col])["count"] == 0]
    print(f"\nFully complete columns: {len(fully_complete)}/{len(headers)}")

    if not results:
        print(f"\nNo columns exceed the null threshold ({threshold * 100:.1f}%).")
    else:
        print(f"\nColumns with missing values (threshold >= {threshold * 100:.1f}%):\n")
        for r in sorted(results, key=lambda x: -x["null_pct"]):
            indicator = "🔴" if r["null_pct"] > 30 else ("🟡" if r["null_pct"] > 10 else "🟢")
            print(f"  {indicator} {r['column']}")
            print(f"     Nulls: {r['null_count']} ({r['null_pct']}%)  |  Type: {r['col_type']}")
            print(f"     Mechanism: {r['mechanism']}")
            print(f"     Strategy:  {r['strategy']}")
            print()

    cooccur = compute_cooccurrence(headers, masks)
    if cooccur:
        print("-" * 64)
        print("NULL CO-OCCURRENCE (top pairs)")
        print("-" * 64)
        for pair in cooccur:
            print(f"  {pair['col_a']} + {pair['col_b']}  →  {pair['co_null_rows']} rows both null")

    print("\n" + "=" * 64)
def main():
    parser = argparse.ArgumentParser(description="Analyze missing values in a CSV dataset.")
    parser.add_argument("--file", required=True, help="Path to CSV file")
    parser.add_argument("--threshold", type=float, default=0.0,
                        help="Only show columns with null fraction above this (e.g. 0.05 = 5%%)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
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
        print("Error: CSV file is empty.", file=sys.stderr)
        sys.exit(1)

    masks = compute_null_mask(headers, rows)

    if args.format == "json":
        output = []
        for col in headers:
            mask = masks[col]
            stats = null_stats(mask)
            raw_vals = [row.get(col, "") for row in rows]
            col_type = infer_type(raw_vals)
            mechanism = classify_mechanism(col, mask, masks)
            strategy = recommend_strategy(stats["pct"], col_type)
            output.append({
                "column": col,
                "null_count": stats["count"],
                "null_pct": stats["pct"],
                "col_type": col_type,
                "mechanism": mechanism,
                "strategy": strategy,
            })
        print(json.dumps({"total_rows": len(rows), "columns": output}, indent=2))
    else:
        print_report(headers, rows, masks, args.threshold)
