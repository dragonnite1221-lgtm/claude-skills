# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dockerfile_analyzer_base import *  # noqa: F403,E402
# fmt: off
from dockerfile_analyzer_p1 import ANTI_PATTERNS  # noqa: E402,E501
from dockerfile_analyzer_p2 import analyze_base_image, analyze_layers, parse_dockerfile  # noqa: E402,E501
# fmt: on


def run_pattern_checks(content, instructions):
    """Run anti-pattern checks."""
    findings = []

    for rule in ANTI_PATTERNS:
        if rule["pattern"] is not None:
            for match in re.finditer(rule["pattern"], content, re.MULTILINE | re.IGNORECASE):
                findings.append({
                    "id": rule["id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "fix": rule["fix"],
                    "line": match.group(0).strip()[:80],
                })

    # Custom checks
    # AP006: Multiple CMD
    cmd_count = sum(1 for i in instructions if i["instruction"] == "CMD")
    if cmd_count > 1:
        r = next(r for r in ANTI_PATTERNS if r["id"] == "AP006")
        findings.append({
            "id": r["id"], "severity": r["severity"],
            "message": r["message"], "fix": r["fix"],
            "line": f"{cmd_count} CMD instructions found",
        })

    # AP009: No USER
    has_user = any(i["instruction"] == "USER" for i in instructions)
    if not has_user and instructions:
        r = next(r for r in ANTI_PATTERNS if r["id"] == "AP009")
        findings.append({
            "id": r["id"], "severity": r["severity"],
            "message": r["message"], "fix": r["fix"],
            "line": "(no USER instruction found)",
        })

    # AP014: No HEALTHCHECK
    has_healthcheck = any(i["instruction"] == "HEALTHCHECK" for i in instructions)
    if not has_healthcheck and instructions:
        r = next(r for r in ANTI_PATTERNS if r["id"] == "AP014")
        findings.append({
            "id": r["id"], "severity": r["severity"],
            "message": r["message"], "fix": r["fix"],
            "line": "(no HEALTHCHECK instruction found)",
        })

    return findings
def generate_report(content, output_format="text", security_focus=False):
    """Generate full analysis report."""
    instructions = parse_dockerfile(content)
    layers = analyze_layers(instructions)
    base = analyze_base_image(instructions)
    findings = run_pattern_checks(content, instructions)

    if security_focus:
        security_ids = {"AP007", "AP009", "AP008"}
        security_severities = {"critical", "high"}
        findings = [f for f in findings if f["id"] in security_ids or f["severity"] in security_severities]

    # Deduplicate findings by id
    seen_ids = set()
    unique_findings = []
    for f in findings:
        key = (f["id"], f["line"])
        if key not in seen_ids:
            seen_ids.add(key)
            unique_findings.append(f)
    findings = unique_findings

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    # Score (100 minus deductions)
    deductions = {"critical": 25, "high": 15, "medium": 5, "low": 2}
    score = max(0, 100 - sum(deductions.get(f["severity"], 0) for f in findings))

    result = {
        "score": score,
        "base_image": base,
        "layers": layers,
        "findings": findings,
        "finding_counts": {
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
        return result

    # Text output
    print(f"\n{'=' * 60}")
    print(f"  Dockerfile Analysis Report")
    print(f"{'=' * 60}")
    print(f"  Score: {score}/100")
    print(f"  Base: {base['image']}:{base['tag']} (~{base['estimated_size_mb']}MB)")
    print(f"  Layers: {layers['total_layers']} | Stages: {layers['stages']} | Multi-stage: {'Yes' if layers['is_multistage'] else 'No'}")
    print(f"  RUN: {layers['run_count']} | COPY: {layers['copy_count']} | ADD: {layers['add_count']}")
    print()

    counts = result["finding_counts"]
    print(f"  Findings: {counts['critical']} critical | {counts['high']} high | {counts['medium']} medium | {counts['low']} low")
    print(f"{'─' * 60}")

    for f in findings:
        icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(f["severity"], "?")
        print(f"\n  [{f['id']}] {icon} {f['severity'].upper()}")
        print(f"  {f['message']}")
        print(f"  Line: {f['line']}")
        print(f"  Fix:  {f['fix']}")

    if not findings:
        print("\n  No issues found. Dockerfile looks good.")

    print(f"\n{'=' * 60}\n")
    return result
