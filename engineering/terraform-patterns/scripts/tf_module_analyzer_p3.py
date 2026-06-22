# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_module_analyzer_base import *  # noqa: F403,E402
# fmt: off
from tf_module_analyzer_p1 import parse_data_sources, parse_resources  # noqa: E402,E501
from tf_module_analyzer_p2 import check_file_structure, check_naming, check_outputs, check_variables, parse_modules, parse_outputs, parse_variables  # noqa: E402,E501
# fmt: on


def analyze_directory(tf_files):
    """Run full analysis on a set of .tf files."""
    all_content = "\n".join(tf_files.values())

    resources = parse_resources(all_content)
    data_sources = parse_data_sources(all_content)
    variables = parse_variables(all_content)
    outputs = parse_outputs(all_content)
    modules = parse_modules(all_content)

    # Collect findings
    findings = []
    findings.extend(check_file_structure(tf_files))
    findings.extend(check_naming(resources, data_sources))
    findings.extend(check_variables(variables))
    findings.extend(check_outputs(outputs))

    # Check for backend configuration
    has_backend = any(
        re.search(r'\bbackend\s+"', content)
        for content in tf_files.values()
    )
    if not has_backend:
        findings.append({
            "severity": "high",
            "message": "No remote backend configured — state is stored locally",
        })

    # Check for terraform required_version
    has_tf_version = any(
        re.search(r'required_version\s*=', content)
        for content in tf_files.values()
    )
    if not has_tf_version:
        findings.append({
            "severity": "medium",
            "message": "No required_version constraint — any Terraform version can be used",
        })

    # Providers in child modules check
    for filename, content in tf_files.items():
        if filename not in ("providers.tf", "versions.tf", "backend.tf"):
            if re.search(r'^provider\s+"', content, re.MULTILINE):
                findings.append({
                    "severity": "medium",
                    "message": f"Provider configuration found in '{filename}' — keep providers in root module only",
                })

    # Sort findings
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    # Unique providers
    providers = sorted(set(r["provider"] for r in resources))

    return {
        "files": sorted(tf_files.keys()),
        "file_count": len(tf_files),
        "resources": resources,
        "resource_count": len(resources),
        "data_sources": data_sources,
        "data_source_count": len(data_sources),
        "variables": variables,
        "variable_count": len(variables),
        "outputs": outputs,
        "output_count": len(outputs),
        "modules": modules,
        "module_count": len(modules),
        "providers": providers,
        "findings": findings,
    }
def generate_report(analysis, output_format="text"):
    """Generate analysis report."""
    findings = analysis["findings"]

    # Score
    deductions = {"critical": 25, "high": 15, "medium": 5, "low": 2}
    score = max(0, 100 - sum(deductions.get(f["severity"], 0) for f in findings))

    counts = {
        "critical": sum(1 for f in findings if f["severity"] == "critical"),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low"),
    }

    result = {
        "score": score,
        "files": analysis["files"],
        "resource_count": analysis["resource_count"],
        "data_source_count": analysis["data_source_count"],
        "variable_count": analysis["variable_count"],
        "output_count": analysis["output_count"],
        "module_count": analysis["module_count"],
        "providers": analysis["providers"],
        "findings": findings,
        "finding_counts": counts,
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
        return result

    # Text output
    print(f"\n{'=' * 60}")
    print(f"  Terraform Module Analysis Report")
    print(f"{'=' * 60}")
    print(f"  Score: {score}/100")
    print(f"  Files: {', '.join(analysis['files'])}")
    print(f"  Providers: {', '.join(analysis['providers']) if analysis['providers'] else 'none detected'}")
    print()
    print(f"  Resources: {analysis['resource_count']} | Data Sources: {analysis['data_source_count']}")
    print(f"  Variables: {analysis['variable_count']} | Outputs: {analysis['output_count']} | Modules: {analysis['module_count']}")
    print()
    print(f"  Findings: {counts['critical']} critical | {counts['high']} high | {counts['medium']} medium | {counts['low']} low")
    print(f"{'─' * 60}")

    for f in findings:
        icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(f["severity"], "?")
        print(f"\n  {icon} {f['severity'].upper()}")
        print(f"  {f['message']}")

    if not findings:
        print("\n  No issues found. Module structure looks good.")

    print(f"\n{'=' * 60}\n")
    return result
