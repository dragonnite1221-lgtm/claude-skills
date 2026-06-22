# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_log_analyzer_base import *  # noqa: F403,E402
# fmt: off
from audit_log_analyzer_p1 import load_logs  # noqa: E402,E501
from audit_log_analyzer_p2 import analyze  # noqa: E402,E501
# fmt: on


def print_human(result, threshold):
    """Print human-readable analysis report."""
    summary = result["summary"]
    anomalies = result["anomalies"]

    print("=== Audit Log Analysis Report ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Anomaly threshold: {threshold}")
    print()

    print("--- Summary ---")
    print(f"  Total log entries:     {summary['total_entries']}")
    print(f"  Unique identities:     {summary['unique_identities']}")
    print(f"  Unique secret paths:   {summary['unique_paths']}")
    print(f"  Unique source IPs:     {summary['unique_source_ips']}")
    print(f"  Total failures:        {summary['total_failures']}")
    print(f"  Off-hours events:      {summary['off_hours_events']}")
    print(f"  Anomalies detected:    {summary['anomalies_found']}")
    print()

    if anomalies:
        print("--- Anomalies ---")
        for i, a in enumerate(anomalies, 1):
            print(f"  [{a['severity']}] {a['type']}: {a['description']}")
        print()
    else:
        print("--- No anomalies detected ---")
        print()

    if result["top_accessed_paths"]:
        print("--- Top Accessed Paths ---")
        for item in result["top_accessed_paths"]:
            print(f"  {item['count']:5d}  {item['path']}")
        print()

    if result["hourly_distribution"]:
        print("--- Hourly Distribution ---")
        max_count = max(result["hourly_distribution"].values()) if result["hourly_distribution"] else 1
        for hour in range(24):
            count = result["hourly_distribution"].get(hour, 0)
            bar_len = int((count / max_count) * 40) if max_count > 0 else 0
            marker = " *" if (hour < 6 or hour >= 22) else ""
            print(f"  {hour:02d}:00  {'#' * bar_len:40s}  {count}{marker}")
        print("  (* = off-hours)")
def main():
    parser = argparse.ArgumentParser(
        description="Analyze Vault/cloud secret manager audit logs for anomalies.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            The analyzer detects:
              - Volume spikes (identity accessing secrets above threshold * average)
              - Multi-IP access (single identity from many source IPs)
              - Failed access attempts (repeated auth/access failures)
              - Off-hours access (before 6 AM or after 10 PM)
              - Broad path access (single identity accessing many distinct paths)

            Log format: JSON lines or JSON array. Each entry should include
            timestamp, auth info, request path/operation, response status,
            and remote address. Missing fields are handled gracefully.

            Examples:
              %(prog)s --log-file vault-audit.log --threshold 5
              %(prog)s --log-file audit.json --threshold 3 --json
        """),
    )
    parser.add_argument("--log-file", required=True, help="Path to audit log file (JSON lines or JSON array)")
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Anomaly sensitivity threshold — lower = more sensitive (default: 5)",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    entries = load_logs(args.log_file)
    if not entries:
        print("No log entries found in file.", file=sys.stderr)
        sys.exit(1)

    result = analyze(entries, args.threshold)
    result["log_file"] = args.log_file
    result["threshold"] = args.threshold
    result["analyzed_at"] = datetime.now().isoformat()

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print_human(result, args.threshold)
