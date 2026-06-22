# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chart_analyzer_base import *  # noqa: F403,E402
# fmt: off
from chart_analyzer_p1 import DEMO_CHART_YAML  # noqa: E402,E501
from chart_analyzer_p2 import DEMO_DEPLOYMENT, DEMO_VALUES_YAML, check_chart_yaml, check_structure, parse_yaml_simple  # noqa: E402,E501
from chart_analyzer_p3 import check_templates  # noqa: E402,E501
from chart_analyzer_p4 import check_security  # noqa: E402,E501
# fmt: on


def analyze_chart(chart_dir, output_format="text", security_focus=False):
    """Run full chart analysis."""
    findings = []
    findings.extend(check_structure(chart_dir))
    findings.extend(check_chart_yaml(chart_dir))
    findings.extend(check_templates(chart_dir))

    if security_focus:
        findings.extend(check_security(chart_dir))
        # Filter to security-relevant items only
        security_ids = {"SC001", "SC002", "SC003", "SC004", "SC005", "SC006", "SC007", "SC008", "SC009"}
        security_severities = {"critical", "high"}
        findings = [f for f in findings if f["id"] in security_ids or f["severity"] in security_severities]
    else:
        findings.extend(check_security(chart_dir))

    # Deduplicate
    seen = set()
    unique = []
    for f in findings:
        key = (f["id"], f.get("line", ""), f.get("file", ""))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    findings = unique

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    # Score
    deductions = {"critical": 25, "high": 15, "medium": 5, "low": 2}
    score = max(0, 100 - sum(deductions.get(f["severity"], 0) for f in findings))

    counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low"),
    }

    # Chart metadata
    chart_yaml_path = chart_dir / "Chart.yaml"
    chart_meta = parse_yaml_simple(chart_yaml_path.read_text(encoding="utf-8")) if chart_yaml_path.exists() else {}

    result = {
        "score": score,
        "chart_name": chart_meta.get("name", chart_dir.name),
        "chart_version": chart_meta.get("version", "unknown"),
        "app_version": chart_meta.get("appVersion", "unknown"),
        "findings": findings,
        "finding_counts": counts,
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
        return result

    # Text output
    print(f"\n{'=' * 60}")
    print(f"  Helm Chart Analysis Report")
    print(f"{'=' * 60}")
    print(f"  Score: {score}/100")
    print(f"  Chart: {result['chart_name']} v{result['chart_version']}")
    print(f"  App Version: {result['app_version']}")
    print()
    print(f"  Findings: {counts['critical']} critical | {counts['high']} high | {counts['medium']} medium | {counts['low']} low")
    print(f"{'─' * 60}")

    for f in findings:
        icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(f["severity"], "?")
        print(f"\n  [{f['id']}] {icon} {f['severity'].upper()}")
        print(f"  {f['message']}")
        if "file" in f:
            print(f"  File: {f['file']}")
        if "line" in f:
            print(f"  Line: {f['line']}")
        print(f"  Fix:  {f['fix']}")

    if not findings:
        print("\n  No issues found. Chart looks good.")

    print(f"\n{'=' * 60}\n")
    return result
def run_demo():
    """Run analysis on demo chart data."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        chart_dir = Path(tmpdir) / "demo-app"
        chart_dir.mkdir()
        (chart_dir / "Chart.yaml").write_text(DEMO_CHART_YAML)
        (chart_dir / "values.yaml").write_text(DEMO_VALUES_YAML)
        templates_dir = chart_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "deployment.yaml").write_text(DEMO_DEPLOYMENT)

        return chart_dir, analyze_chart
