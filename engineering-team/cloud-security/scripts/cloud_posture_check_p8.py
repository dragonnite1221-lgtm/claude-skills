# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402
# fmt: off
from cloud_posture_check_p2 import IAMAnalysisResult, IAMFinding  # noqa: E402,E501
from cloud_posture_check_p7 import _csd_2, print_text_report, result_to_dict  # noqa: E402,E501
# fmt: on


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cloud Security Posture Check — IAM, S3, and Security Group analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s policy.json
  %(prog)s policy.json --check privilege-escalation --json
  %(prog)s policy.json --check data-exfil --severity-modifier regulated-data --json
  %(prog)s policy.json --check public-exposure --json
  %(prog)s bucket.json --check s3 --severity-modifier internet-facing --json
  %(prog)s sg.json --check sg --provider aws --json
  %(prog)s policy.json --check all --json

Exit codes:
  0  No findings or informational only
  1  High-severity findings present
  2  Critical findings present
        """,
    )

    parser.add_argument(
        "input_file",
        help="Path to JSON file (IAM policy, S3 config, or Security Group JSON)",
    )
    parser.add_argument(
        "--check",
        choices=["privilege-escalation", "data-exfil", "public-exposure", "s3", "sg", "all"],
        default="privilege-escalation",
        help="Check mode to run (default: privilege-escalation)",
    )
    parser.add_argument(
        "--provider",
        choices=["aws", "azure", "gcp"],
        default="aws",
        help="Cloud provider (default: aws; Azure/GCP: only IAM checks available)",
    )
    parser.add_argument(
        "--severity-modifier",
        choices=["internet-facing", "regulated-data", "none"],
        default="none",
        dest="severity_modifier",
        help="Bump all finding severities +1 band (default: none)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write JSON output to file",
    )

    args = parser.parse_args()

    # --- Load input file ---
    try:
        with open(args.input_file, "r", encoding="utf-8") as fh:
            policy_data = json.load(fh)
    except FileNotFoundError:
        err = {"error": f"File not found: {args.input_file}"}
        if args.json:
            print(json.dumps(err, indent=2))
        else:
            print(f"Error: {err['error']}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        err = {"error": f"Invalid JSON: {exc}"}
        if args.json:
            print(json.dumps(err, indent=2))
        else:
            print(f"Error: {err['error']}", file=sys.stderr)
        sys.exit(1)

    source = args.input_file
    severity_modifier = args.severity_modifier
    provider = args.provider

    # --- Gate S3 / SG checks by provider ---
    check_mode = args.check

    if check_mode in ("s3", "sg") and provider != "aws":
        msg = (
            f"Azure/GCP checks coming soon — "
            f"use --provider aws for S3/SG analysis"
        )
        if args.json:
            print(json.dumps({"message": msg, "provider": provider, "check_mode": check_mode}, indent=2))
        else:
            print(msg)
        sys.exit(0)

    # --- Run checks ---
    all_results: List[IAMAnalysisResult] = []

    iam_check_modes = ["privilege-escalation", "data-exfil", "public-exposure"]

    r = _csd_2(all_results, check_mode, iam_check_modes, policy_data, provider, severity_modifier, source)

    # --- Flatten findings for output when multiple checks run ---
    if len(all_results) == 1:
        combined_result = all_results[0]
    else:
        # Merge into a single result
        all_findings: List[IAMFinding] = []
        for res in all_results:
            all_findings.extend(res.findings)

        combined_result = IAMAnalysisResult(
            source=source,
            check_mode=check_mode,
            provider=provider,
            severity_modifier=severity_modifier,
        )
        combined_result.findings = all_findings
        combined_result.summary = {
            "total_findings": len(all_findings),
            "critical": sum(1 for f in all_findings if f.severity == "critical"),
            "high": sum(1 for f in all_findings if f.severity == "high"),
            "medium": sum(1 for f in all_findings if f.severity == "medium"),
            "low": sum(1 for f in all_findings if f.severity == "low"),
            "check_mode": check_mode,
            "provider": provider,
            "severity_modifier": severity_modifier,
            "checks_run": [r.check_mode for r in all_results],
        }

    # --- Output ---
    if args.json or args.output:
        output_dict = result_to_dict(combined_result)
        json_str = json.dumps(output_dict, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(json_str)
            if not args.json:
                print(f"Results written to {args.output}")
        if args.json:
            print(json_str)
    else:
        print_text_report(combined_result)

    # --- Exit code ---
    if combined_result.critical_count > 0:
        sys.exit(2)
    if combined_result.high_count > 0:
        sys.exit(1)
    sys.exit(0)
