# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ai_threat_scanner_base import *  # noqa: F403,E402
# fmt: off
from ai_threat_scanner_p1 import SEED_PROMPTS  # noqa: E402,E501
from ai_threat_scanner_p2 import MODEL_INVERSION_RISK, build_test_coverage, compute_overall_risk, list_patterns, scan_prompts  # noqa: E402,E501
from ai_threat_scanner_p3 import _csd_0, _csd_1, build_recommendations  # noqa: E402,E501
from ai_threat_scanner_p4 import _csd_2  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="AI/LLM Security Threat Scanner — Detects prompt injection, jailbreaks, and ATLAS threats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 ai_threat_scanner.py --target-type llm --access-level black-box --json\n"
            "  python3 ai_threat_scanner.py --target-type llm --test-file prompts.json "
            "--access-level gray-box --authorized --json\n"
            "  python3 ai_threat_scanner.py --list-patterns\n"
            "\nExit codes:\n"
            "  0  Low risk — no critical findings\n"
            "  1  Medium/High risk findings detected\n"
            "  2  Critical findings or missing authorization for invasive tests"
        ),
    )
    parser.add_argument(
        "--target-type",
        choices=["llm", "classifier", "embedding"],
        default="llm",
        help="Type of AI system being assessed (default: llm)",
    )
    parser.add_argument(
        "--access-level",
        choices=["black-box", "gray-box", "white-box"],
        default="black-box",
        help="Attacker access level to the model (default: black-box)",
    )
    parser.add_argument(
        "--test-file",
        type=str,
        dest="test_file",
        help="Path to JSON file containing an array of prompt strings to scan",
    )
    parser.add_argument(
        "--scope",
        type=str,
        default="",
        help=(
            "Comma-separated scan scope. Options: prompt-injection, jailbreak, model-inversion, "
            "data-poisoning, tool-abuse. Default: all."
        ),
    )
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="Confirms authorization to conduct invasive (gray-box / white-box) tests",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="Print all injection signature names with severity and ATLAS IDs, then exit",
    )

    args = parser.parse_args()

    if args.list_patterns:
        list_patterns()  # exits internally

    # Parse scope
    scope_set = set()
    if args.scope:
        valid_scopes = {"prompt-injection", "jailbreak", "model-inversion", "data-poisoning", "tool-abuse"}
        for s in args.scope.split(","):
            s = s.strip()
            if s:
                if s not in valid_scopes:
                    print(
                        f"WARNING: Unknown scope value '{s}'. Valid values: {', '.join(sorted(valid_scopes))}",
                        file=sys.stderr,
                    )
                else:
                    scope_set.add(s)

    # Authorization check for invasive access levels
    auth_required = False
    if args.access_level in ("white-box", "gray-box") and not args.authorized:
        auth_required = True

    # Load prompts
    prompts = SEED_PROMPTS
    prompts = _csd_1(args, prompts)

    # Scan prompts
    # Filter scope: data-poisoning and model-inversion are checked separately,
    # not part of pattern scanning
    pattern_scope = scope_set - {"model-inversion", "data-poisoning"} if scope_set else set()
    findings, injection_score, matched_atlas_ids = scan_prompts(prompts, pattern_scope if pattern_scope else None)

    # Data poisoning check: scan if target-type != llm OR scope includes data-poisoning
    data_poisoning_in_scope = (
        not scope_set  # all in scope
        or "data-poisoning" in scope_set
        or args.target_type != "llm"
    )
    if data_poisoning_in_scope:
        dp_scope = {"data-poisoning"}
        dp_findings, _, dp_atlas = scan_prompts(prompts, dp_scope)
        # Merge without duplicates
        existing_ids = {id(f) for f in findings}
        for f in dp_findings:
            if id(f) not in existing_ids:
                findings.append(f)
        matched_atlas_ids = list(set(matched_atlas_ids) | set(dp_atlas))

    # Model inversion risk assessment
    inversion_check = MODEL_INVERSION_RISK.get(args.access_level, MODEL_INVERSION_RISK["black-box"])
    model_inversion_risk = {
        "access_level": args.access_level,
        "risk": inversion_check["risk"],
        "description": inversion_check["description"],
        "in_scope": not scope_set or "model-inversion" in scope_set,
    }

    # Authorization finding
    authorization_check = {
        "access_level": args.access_level,
        "authorized": args.authorized,
        "auth_required": auth_required,
        "note": (
            "Invasive access levels (gray-box, white-box) require explicit written authorization. "
            "Ensure signed testing agreement is in place before proceeding."
            if auth_required
            else "Authorization requirement satisfied."
        ),
    }

    # If auth required, inject a critical finding
    _csd_2(args, auth_required, findings)

    # Overall risk
    overall_risk = compute_overall_risk(findings, auth_required, args.access_level)

    # Test coverage
    test_coverage = build_test_coverage(matched_atlas_ids)

    # Recommendations
    recommendations = build_recommendations(
        findings, overall_risk, args.access_level, args.target_type, auth_required
    )

    # Assemble output
    output = {
        "target_type": args.target_type,
        "access_level": args.access_level,
        "prompts_tested": len(prompts),
        "injection_score": injection_score,
        "findings": findings,
        "model_inversion_risk": model_inversion_risk,
        "overall_risk": overall_risk,
        "test_coverage": test_coverage,
        "authorization_check": authorization_check,
        "recommendations": recommendations,
    }

    _csd_0(args, auth_required, findings, inversion_check, output, recommendations, test_coverage)

    # Exit codes
    if overall_risk == "critical" or auth_required:
        sys.exit(2)
    elif overall_risk in ("high", "medium"):
        sys.exit(1)
    sys.exit(0)
