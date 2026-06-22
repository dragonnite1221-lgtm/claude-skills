# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_signal_analyzer_base import *  # noqa: F403,E402
# fmt: off
from threat_signal_analyzer_p1 import hunt_mode  # noqa: E402,E501
from threat_signal_analyzer_p2 import ioc_mode  # noqa: E402,E501
from threat_signal_analyzer_p3 import anomaly_mode  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Threat Signal Analyzer — Hunt hypothesis scoring, IOC sweep planning, "
            "and behavioral anomaly detection."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 threat_signal_analyzer.py --mode hunt --hypothesis 'APT using WMI for lateral movement' --json\n"
            "  python3 threat_signal_analyzer.py --mode ioc --ioc-file iocs.json --ioc-date 2026-01-15 --json\n"
            "  python3 threat_signal_analyzer.py --mode anomaly --events-file events.json "
            "--baseline-mean 45.0 --baseline-std 12.0 --json\n"
            "\nExit codes:\n"
            "  0  No high-priority findings\n"
            "  1  Medium-priority signals detected\n"
            "  2  High-priority findings confirmed"
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["hunt", "ioc", "anomaly"],
        required=True,
        help="Analysis mode: hunt | ioc | anomaly",
    )
    # Hunt args
    parser.add_argument("--hypothesis", type=str, help="[hunt] Free-text threat hypothesis")
    parser.add_argument("--actor-relevance", type=int, choices=[0, 1, 2, 3], default=1,
                        dest="actor_relevance",
                        help="[hunt] Actor relevance score 0-3 (default: 1)")
    parser.add_argument("--control-gap", type=int, choices=[0, 1, 2, 3], default=1,
                        dest="control_gap",
                        help="[hunt] Security control gap score 0-3 (default: 1)")
    parser.add_argument("--data-availability", type=int, choices=[0, 1, 2, 3], default=2,
                        dest="data_availability",
                        help="[hunt] Data availability score 0-3 (default: 2)")
    # IOC args
    parser.add_argument("--ioc-file", type=str, dest="ioc_file",
                        help="[ioc] Path to JSON file with IOC lists (keys: ips, domains, hashes, urls, emails)")
    parser.add_argument("--ioc-date", type=str, dest="ioc_date",
                        help="[ioc] Date IOCs were collected (YYYY-MM-DD) for freshness check")
    # Anomaly args
    parser.add_argument("--events-file", type=str, dest="events_file",
                        help="[anomaly] Path to JSON array of events with {timestamp, entity, action, volume}")
    parser.add_argument("--baseline-mean", type=float, dest="baseline_mean",
                        help="[anomaly] Baseline mean for volume z-score calculation")
    parser.add_argument("--baseline-std", type=float, dest="baseline_std",
                        help="[anomaly] Baseline standard deviation for z-score calculation")
    # Output
    parser.add_argument("--json", action="store_true", dest="output_json",
                        help="Output results as JSON")

    args = parser.parse_args()

    if args.mode == "hunt":
        if not args.hypothesis:
            parser.error("--hypothesis is required for hunt mode")
        result = hunt_mode(args)
        priority_score = result.get("priority_score", 0)
        if args.output_json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== THREAT HUNT ANALYSIS ===")
            print(f"Hypothesis      : {result['hypothesis']}")
            print(f"Matched Keywords: {', '.join(result['matched_keywords']) or 'None'}")
            print(f"Matched T-Codes : {', '.join(result['matched_tcodes']) or 'None'}")
            print(f"Tactics         : {', '.join(result['tactics']) or 'None'}")
            print(f"Priority Score  : {priority_score} (threshold: {result['score_breakdown']['pursue_threshold']})")
            print(f"Pursue?         : {'YES' if result['pursue_recommendation'] else 'NO'}")
            print(f"Data Sources    : {', '.join(result['data_sources_required']) or 'None identified'}")
            print(f"Quality Check   : {'Required' if result['data_quality_check_required'] else 'Not required'}")
        # Exit codes: >= 8 = high, 5-7 = medium, < 5 = low
        if priority_score >= 8:
            sys.exit(2)
        elif priority_score >= 5:
            sys.exit(1)
        sys.exit(0)

    elif args.mode == "ioc":
        if not args.ioc_file:
            parser.error("--ioc-file is required for ioc mode")
        result = ioc_mode(args)
        if "error" in result:
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.output_json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== IOC SWEEP PLAN ===")
            print(f"IOC Counts      : {result['ioc_counts']}")
            print(f"Coverage Score  : {result['coverage_score']:.2%}")
            print(f"Freshness Warn  : {'YES — IOCs may be stale' if result['freshness_warning'] else 'No'}")
            if result.get("ioc_age_days") is not None:
                print(f"IOC Age (days)  : {result['ioc_age_days']}")
            print(f"\nAction: {result['recommended_action']}")
            print("\nSweep Plan:")
            for ioc_type, plan in result["sweep_plan"].items():
                stale_tag = " [STALE]" if plan["stale"] else ""
                print(f"  {ioc_type:<12} {plan['count']} IOC(s){stale_tag} -> {', '.join(plan['targets'])}")
        # Exit codes based on staleness and coverage
        if result["freshness_warning"]:
            sys.exit(1)
        if result["coverage_score"] >= 0.5 and not result["freshness_warning"]:
            sys.exit(0)
        sys.exit(1)

    elif args.mode == "anomaly":
        if not args.events_file:
            parser.error("--events-file is required for anomaly mode")
        if args.baseline_mean is None or args.baseline_std is None:
            parser.error("--baseline-mean and --baseline-std are required for anomaly mode")
        result = anomaly_mode(args)
        if "error" in result:
            if args.output_json:
                print(json.dumps(result, indent=2))
            else:
                print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.output_json:
            print(json.dumps(result, indent=2))
        else:
            print("\n=== ANOMALY DETECTION REPORT ===")
            print(f"Total Events    : {result['total_events']}")
            print(f"Baseline Mean   : {result['baseline_mean']}")
            print(f"Baseline Std    : {result['baseline_std']}")
            print(f"Hard Flags      : {result['hard_flag_count']} (z >= 3.0)")
            print(f"Soft Flags      : {result['soft_flag_count']} (z >= 2.0)")
            print(f"Time Anomalies  : {result['time_anomaly_count']}")
            print(f"Risk Score      : {result['risk_score']:.4f}")
            if result["top_anomalous_entities"]:
                print("\nTop Anomalous Entities:")
                for entry in result["top_anomalous_entities"]:
                    print(f"  {entry['entity']}: {entry['anomaly_count']} anomaly(s)")
            print(f"\nAction: {result['recommended_action']}")
            if result["anomaly_events"]:
                print("\nFlagged Events (first 10):")
                for ev in result["anomaly_events"][:10]:
                    flags = []
                    if ev["hard_flag"]:
                        flags.append("HARD")
                    if ev["soft_flag"]:
                        flags.append("SOFT")
                    if ev["time_anomaly"]:
                        flags.append("TIME")
                    print(
                        f"  [{', '.join(flags)}] entity={ev['entity']} "
                        f"volume={ev['volume']} z={ev['z_score']} ts={ev['timestamp']}"
                    )
        # Exit codes
        hard_flags = result.get("hard_flag_count", 0)
        soft_flags = result.get("soft_flag_count", 0)
        time_anomalies = result.get("time_anomaly_count", 0)
        if hard_flags > 0:
            sys.exit(2)
        elif soft_flags > 0 or time_anomalies > 0:
            sys.exit(1)
        sys.exit(0)
