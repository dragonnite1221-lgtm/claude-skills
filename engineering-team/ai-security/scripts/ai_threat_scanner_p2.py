# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ai_threat_scanner_base import *  # noqa: F403,E402
# fmt: off
from ai_threat_scanner_p1 import ATLAS_TECHNIQUE_MAP, INJECTION_SIGNATURES  # noqa: E402,E501
# fmt: on


MODEL_INVERSION_RISK = {
    "white-box": {
        "risk": "critical",
        "description": "Direct model weight access enables gradient-based inversion attacks",
    },
    "gray-box": {
        "risk": "high",
        "description": "Confidence scores enable membership inference and partial inversion",
    },
    "black-box": {
        "risk": "low",
        "description": "Limited to output-based attacks; requires many queries to extract information",
    },
}
SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "informational": 0}
def list_patterns():
    """Print all INJECTION_SIGNATURES with severity and ATLAS ID, then exit."""
    print(f"\n{'Signature':<28} {'Severity':<10} {'ATLAS ID':<18} Description")
    print("-" * 95)
    for sig_name, sig_data in INJECTION_SIGNATURES.items():
        print(
            f"{sig_name:<28} {sig_data['severity']:<10} {sig_data['atlas_id']:<18} {sig_data['description']}"
        )
    print()
    sys.exit(0)
def _sig_in_scope(sig_name, scope_set):
    """Determine whether a signature belongs to the active scope."""
    scope_map = {
        "direct_role_override": "prompt-injection",
        "indirect_injection": "prompt-injection",
        "jailbreak_persona": "jailbreak",
        "system_prompt_extraction": "prompt-injection",
        "tool_abuse": "tool-abuse",
        "data_poisoning_marker": "data-poisoning",
    }
    if not scope_set:
        return True  # all in scope
    sig_scope = scope_map.get(sig_name)
    return sig_scope in scope_set
def scan_prompts(prompts, scope_set):
    """
    Scan each prompt against all INJECTION_SIGNATURES that are in scope.
    Returns (findings, injection_score, matched_atlas_ids).
    """
    findings = []
    total_sigs = sum(
        1 for sig_name in INJECTION_SIGNATURES
        if _sig_in_scope(sig_name, scope_set)
    )
    matched_sig_names = set()

    for prompt in prompts:
        prompt_excerpt = prompt[:100]
        for sig_name, sig_data in INJECTION_SIGNATURES.items():
            if not _sig_in_scope(sig_name, scope_set):
                continue
            for pattern in sig_data["patterns"]:
                if re.search(pattern, prompt, re.IGNORECASE):
                    matched_sig_names.add(sig_name)
                    findings.append({
                        "prompt_excerpt": prompt_excerpt,
                        "signature_name": sig_name,
                        "atlas_id": sig_data["atlas_id"],
                        "atlas_name": sig_data["atlas_name"],
                        "severity": sig_data["severity"],
                        "description": sig_data["description"],
                        "matched_pattern": pattern,
                    })
                    break  # one match per signature per prompt is enough

    injection_score = round(len(matched_sig_names) / total_sigs, 4) if total_sigs > 0 else 0.0
    matched_atlas_ids = list({f["atlas_id"] for f in findings})
    return findings, injection_score, matched_atlas_ids
def build_test_coverage(matched_atlas_ids):
    """Return a dict indicating which ATLAS techniques were covered vs not tested."""
    coverage = {}
    for atlas_id, tech_data in ATLAS_TECHNIQUE_MAP.items():
        if atlas_id in matched_atlas_ids:
            coverage[tech_data["name"]] = "covered"
        else:
            coverage[tech_data["name"]] = "not_tested"
    return coverage
def compute_overall_risk(findings, auth_required, inversion_risk_level):
    """Compute overall risk level from findings and context."""
    severity_levels = [SEVERITY_ORDER.get(f["severity"], 0) for f in findings]
    if auth_required:
        severity_levels.append(SEVERITY_ORDER["critical"])
    # Factor in model inversion risk
    inversion_severity = MODEL_INVERSION_RISK.get(inversion_risk_level, {}).get("risk", "low")
    severity_levels.append(SEVERITY_ORDER.get(inversion_severity, 0))

    if not severity_levels:
        return "low"
    max_level = max(severity_levels)
    for label, val in SEVERITY_ORDER.items():
        if val == max_level:
            return label
    return "low"
