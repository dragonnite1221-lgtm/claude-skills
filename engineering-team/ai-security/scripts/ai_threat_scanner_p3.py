# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ai_threat_scanner_base import *  # noqa: F403,E402
# fmt: off
from ai_threat_scanner_p1 import SEED_PROMPTS  # noqa: E402,E501
# fmt: on


def build_recommendations(findings, overall_risk, access_level, target_type, auth_required):
    """Build a prioritised recommendations list from findings."""
    recs = []
    seen = set()

    severity_seen = {f["severity"] for f in findings}

    if auth_required:
        recs.append(
            "CRITICAL: Obtain written authorization before conducting gray-box or white-box testing. "
            "Use --authorized only after legal sign-off is confirmed."
        )

    if "critical" in severity_seen:
        recs.append(
            "Deploy prompt injection guardrails (input validation, output filtering) as highest priority. "
            "Consider a dedicated safety classifier layer before LLM inference."
        )
    if "tool_abuse" in {f["signature_name"] for f in findings}:
        recs.append(
            "Implement tool-call approval gates for all agent-invoked actions. "
            "Require human confirmation for any destructive or data-exfiltrating tool call."
        )
    if "system_prompt_extraction" in {f["signature_name"] for f in findings}:
        recs.append(
            "Harden system prompt confidentiality: instruct model to refuse prompt-reveal requests, "
            "and consider system prompt encryption or separation from user-turn context."
        )
    if access_level in ("white-box", "gray-box"):
        recs.append(
            "Restrict model API access: disable logit/probability outputs in production to reduce "
            "membership inference and model inversion attack surface."
        )
    if target_type == "classifier":
        recs.append(
            "Run adversarial robustness evaluation (ART / Foolbox) against the classifier. "
            "Implement adversarial training or input denoising to improve resistance to AML.T0043."
        )
    if target_type == "embedding":
        recs.append(
            "Audit embedding API for model inversion risk; enforce rate limits and monitor "
            "for high-volume embedding extraction consistent with AML.T0024."
        )
    if not findings:
        recs.append(
            "No injection patterns detected in tested prompts. "
            "Expand test coverage with domain-specific adversarial prompts and red-team iterations."
        )

    # Deduplicate while preserving order
    final_recs = []
    for rec in recs:
        if rec not in seen:
            seen.add(rec)
            final_recs.append(rec)
    return final_recs
def _csd_0(args, auth_required, findings, inversion_check, output, recommendations, test_coverage):
    if args.output_json:
        print(json.dumps(output, indent=2))
    else:
        print("\n=== AI/LLM THREAT SCAN REPORT ===")
        print(f"Target Type     : {output['target_type']}")
        print(f"Access Level    : {output['access_level']}")
        print(f"Prompts Tested  : {output['prompts_tested']}")
        print(f"Injection Score : {output['injection_score']:.2%}")
        print(f"Overall Risk    : {output['overall_risk'].upper()}")
        print(f"Auth Required   : {'YES — obtain authorization before proceeding' if auth_required else 'No'}")

        print(f"\nModel Inversion : [{inversion_check['risk'].upper()}] {inversion_check['description']}")

        if findings:
            non_auth_findings = [f for f in findings if f["signature_name"] != "authorization_required"]
            print(f"\nFindings ({len(non_auth_findings)}):")
            seen_sigs = set()
            for f in non_auth_findings:
                sig = f["signature_name"]
                if sig not in seen_sigs:
                    seen_sigs.add(sig)
                    print(
                        f"  [{f['severity'].upper()}] {f['signature_name']} "
                        f"({f['atlas_id']}) — {f['description']}"
                    )
                    print(f"    Excerpt: {f['prompt_excerpt'][:80]}...")
        else:
            print("\nFindings: None detected.")

        print("\nTest Coverage:")
        for tech_name, status in test_coverage.items():
            print(f"  {tech_name:<45} {status}")

        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
        print()
def _csd_1(args, prompts):
    if args.test_file:
        try:
            with open(args.test_file, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if not isinstance(loaded, list):
                print("ERROR: --test-file must contain a JSON array of strings.", file=sys.stderr)
                sys.exit(2)
            # Accept both plain strings and objects with a "prompt" key
            prompts = []
            for item in loaded:
                if isinstance(item, str):
                    prompts.append(item)
                elif isinstance(item, dict) and "prompt" in item:
                    prompts.append(str(item["prompt"]))
            if not prompts:
                print("WARNING: No prompts loaded from test file; falling back to seed prompts.", file=sys.stderr)
                prompts = SEED_PROMPTS
        except FileNotFoundError:
            print(f"ERROR: Test file not found: {args.test_file}", file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Invalid JSON in test file: {exc}", file=sys.stderr)
            sys.exit(2)
    return prompts
