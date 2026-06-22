# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_triage_base import *  # noqa: F403,E402
# fmt: off
from incident_triage_p1 import INCIDENT_TAXONOMY  # noqa: E402,E501
from incident_triage_p2 import parse_forensic_fields  # noqa: E402,E501
from incident_triage_p3 import assess_dwell_severity, build_ioc_summary  # noqa: E402,E501
from incident_triage_p4 import _escalate_sev, check_false_positives, check_sev_escalation_triggers, classify_incident, get_escalation_path  # noqa: E402,E501
from incident_triage_p5 import _csd_0, _print_text_report  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Incident Classification, Triage, and Escalation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  echo '{"event_type": "ransomware"}' | %(prog)s --json
  %(prog)s --input event.json --classify --false-positive-check --json
  %(prog)s --input event.json --severity sev1 --json

Exit codes:
  0  SEV3/SEV4 or no confirmed incident
  1  SEV2 — elevated response required
  2  SEV1 — critical incident declared
        """,
    )

    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="JSON file path containing the security event (default: stdin)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--classify",
        action="store_true",
        help="Run incident classification against INCIDENT_TAXONOMY",
    )
    parser.add_argument(
        "--false-positive-check",
        action="store_true",
        dest="false_positive_check",
        help="Run false positive filter checks",
    )
    parser.add_argument(
        "--severity",
        choices=["sev1", "sev2", "sev3", "sev4"],
        help="Explicit severity override (skips taxonomy-derived severity)",
    )

    args = parser.parse_args()

    # --- Load input ---
    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as fh:
                raw_event = json.load(fh)
        else:
            raw_event = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        msg = {"error": f"Invalid JSON input: {exc}"}
        if args.json:
            print(json.dumps(msg, indent=2))
        else:
            print(f"Error: {msg['error']}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        msg = {"error": str(exc)}
        if args.json:
            print(json.dumps(msg, indent=2))
        else:
            print(f"Error: {msg['error']}", file=sys.stderr)
        sys.exit(1)

    # --- Forensic pre-analysis (base logic) ---
    fields = parse_forensic_fields(raw_event)
    ioc_summary = build_ioc_summary(fields)

    forensic_analysis = {
        "source_ip": fields["source_ip"],
        "destination_ip": fields["destination_ip"],
        "user_account": fields["user_account"],
        "hostname": fields["hostname"],
        "process_name": fields["process_name"],
        "dwell_hours": fields["dwell_hours"],
        "dwell_severity": assess_dwell_severity(fields["dwell_hours"]),
    }

    # --- Classification ---
    incident_type = "unknown"
    confidence = 0.0

    if args.classify or not args.severity:
        incident_type, confidence = classify_incident(raw_event)

    # Override with explicit event_type if classify not run
    if not args.classify:
        et = str(raw_event.get("event_type", "")).lower().replace(" ", "_").replace("-", "_")
        if et in INCIDENT_TAXONOMY:
            incident_type = et
            confidence = 0.75

    # --- Determine base severity ---
    if args.severity:
        severity = args.severity.lower()
    else:
        taxonomy_entry = INCIDENT_TAXONOMY.get(incident_type, {})
        severity = taxonomy_entry.get("default_severity", "sev4")

        # Factor in dwell severity
        dwell_sev_map = {"critical": "sev1", "high": "sev2", "medium": "sev3", "low": "sev4"}
        dwell_derived = dwell_sev_map.get(forensic_analysis["dwell_severity"], "sev4")
        severity = _escalate_sev(severity, dwell_derived)

    # --- Escalation trigger check ---
    escalation_trigger_fired: Optional[str] = None
    trigger_result = check_sev_escalation_triggers(raw_event)
    if trigger_result:
        escalation_trigger_fired = trigger_result
        severity = _escalate_sev(severity, trigger_result)

    # --- False positive check ---
    fp_indicators: List[str] = []
    if args.false_positive_check:
        fp_indicators = check_false_positives(raw_event)

    # --- Escalation path ---
    escalation_path = get_escalation_path(incident_type, severity)

    # --- Recommended action ---
    recommended_action = _csd_0(fp_indicators, severity)

    # --- Assemble output ---
    result: Dict[str, Any] = {
        "incident_type": incident_type,
        "classification_confidence": confidence,
        "severity": severity,
        "false_positive_indicators": fp_indicators,
        "escalation_trigger_fired": escalation_trigger_fired,
        "escalation_path": escalation_path,
        "forensic_analysis": forensic_analysis,
        "ioc_summary": ioc_summary,
        "recommended_action": recommended_action,
        "taxonomy": INCIDENT_TAXONOMY.get(incident_type, {}),
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # --- Output ---
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_text_report(result)

    # --- Exit code ---
    if severity == "sev1":
        sys.exit(2)
    elif severity == "sev2":
        sys.exit(1)
    else:
        sys.exit(0)
