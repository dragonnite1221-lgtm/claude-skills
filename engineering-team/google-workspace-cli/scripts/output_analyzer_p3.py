# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from output_analyzer_base import *  # noqa: F403,E402
# fmt: off
from output_analyzer_p1 import DEMO_DATA, apply_filter, apply_group_by, apply_select, apply_sort, read_input  # noqa: E402,E501
from output_analyzer_p2 import compute_stats, format_csv_output, format_table  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Parse, filter, and aggregate JSON/NDJSON from gws CLI output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gws drive files list --json | %(prog)s --count
  gws drive files list --json | %(prog)s --filter "mimeType=pdf" --select "name,size"
  gws drive files list --json | %(prog)s --group-by "mimeType" --format table
  gws drive files list --json | %(prog)s --sort "size" --reverse --format table
  gws drive files list --json | %(prog)s --stats "size"
  %(prog)s --input results.json --select "name,mimeType" --format csv
  %(prog)s --demo --select "name,mimeType,size" --format table
        """,
    )
    parser.add_argument("--input", help="Input file (default: stdin)")
    parser.add_argument("--demo", action="store_true", help="Use demo data")
    parser.add_argument("--count", action="store_true", help="Count records")
    parser.add_argument("--filter", help="Filter by field=value")
    parser.add_argument("--select", help="Comma-separated fields to project")
    parser.add_argument("--sort", help="Sort by field")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order")
    parser.add_argument("--group-by", help="Group by field and count")
    parser.add_argument("--stats", help="Compute stats for a numeric field")
    parser.add_argument("--format", choices=["json", "table", "csv"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--json", action="store_true",
                        help="Shorthand for --format json")
    args = parser.parse_args()

    if args.json:
        args.format = "json"

    # Read input
    if args.demo:
        records = DEMO_DATA[:]
    else:
        records = read_input(args.input)

    if not records and not args.demo:
        # If no pipe input and no file, use demo
        records = DEMO_DATA[:]
        print("(No input detected, using demo data)\n", file=sys.stderr)

    # Apply operations in order
    if args.filter:
        records = apply_filter(records, args.filter)

    if args.sort:
        records = apply_sort(records, args.sort, args.reverse)

    # Count
    if args.count:
        if args.format == "json":
            print(json.dumps({"count": len(records)}))
        else:
            print(f"Count: {len(records)}")
        return

    # Group by
    if args.group_by:
        groups = apply_group_by(records, args.group_by)
        if args.format == "json":
            print(json.dumps(groups, indent=2))
        elif args.format == "csv":
            print(f"{args.group_by},count")
            for k, v in groups.items():
                print(f"{k},{v}")
        else:
            print(f"\n  Group by: {args.group_by}\n")
            for k, v in groups.items():
                print(f"  {k:<50} {v}")
            print(f"\n  Total groups: {len(groups)}")
        return

    # Stats
    if args.stats:
        stats = compute_stats(records, args.stats)
        if args.format == "json":
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n  Stats for '{args.stats}':")
            for k, v in stats.items():
                if isinstance(v, float):
                    print(f"    {k}: {v:,.2f}")
                else:
                    print(f"    {k}: {v}")
        return

    # Select fields
    if args.select:
        records = apply_select(records, args.select)

    # Output
    if args.format == "json":
        print(json.dumps(records, indent=2))
    elif args.format == "csv":
        print(format_csv_output(records))
    else:
        print(f"\n{format_table(records)}\n")
        print(f"  ({len(records)} records)\n")
