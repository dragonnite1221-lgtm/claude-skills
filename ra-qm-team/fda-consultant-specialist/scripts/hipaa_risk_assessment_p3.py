# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hipaa_risk_assessment_base import *  # noqa: F403,E402
# fmt: off
from hipaa_risk_assessment_p2 import VULNERABILITY_PATTERNS, scan_code_patterns, scan_documentation  # noqa: E402,E501
# fmt: on


def detect_security_vulnerabilities(project_dir: Path) -> List[Dict]:
    """Scan for security vulnerabilities."""
    vulnerabilities = []
    code_extensions = ["*.py", "*.js", "*.ts", "*.java", "*.cs", "*.go", "*.yaml", "*.yml", "*.json"]

    for ext in code_extensions:
        try:
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(skip in str(file_path) for skip in ["node_modules", "venv", ".venv", "__pycache__", ".git"]):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    rel_path = str(file_path.relative_to(project_dir))

                    for pattern, vuln_type in VULNERABILITY_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            vulnerabilities.append({
                                "file": rel_path,
                                "vulnerability": vuln_type,
                                "count": len(matches)
                            })
                except Exception:
                    continue
        except Exception:
            continue

    return vulnerabilities
def assess_control(project_dir: Path, control_id: str, control_data: Dict) -> Dict:
    """Assess a single HIPAA control."""
    doc_evidence = scan_documentation(project_dir, control_data["doc_patterns"])
    code_evidence = scan_code_patterns(project_dir, control_data["code_patterns"]) if control_data["code_patterns"] else []

    # Determine compliance status
    has_docs = len(doc_evidence) > 0
    has_code = len(code_evidence) > 0

    if has_docs and (has_code or not control_data["code_patterns"]):
        status = "implemented"
        score = 100
    elif has_docs or has_code:
        status = "partial"
        score = 50
    else:
        status = "gap"
        score = 0

    return {
        "control_id": control_id,
        "title": control_data["title"],
        "requirement": control_data["requirement"],
        "status": status,
        "score": score,
        "weight": control_data["weight"],
        "weighted_score": (score * control_data["weight"]) / 100,
        "documentation": doc_evidence,
        "code_evidence": [e["file"] for e in code_evidence]
    }
def assess_category(project_dir: Path, category_id: str, category_data: Dict) -> Dict:
    """Assess a HIPAA safeguard category."""
    control_results = []
    total_weight = 0
    weighted_score = 0

    for control_id, control_data in category_data["controls"].items():
        result = assess_control(project_dir, control_id, control_data)
        control_results.append(result)
        total_weight += control_data["weight"]
        weighted_score += result["weighted_score"]

    category_score = round((weighted_score / total_weight) * 100, 1) if total_weight > 0 else 0

    return {
        "category": category_id,
        "title": category_data["title"],
        "score": category_score,
        "controls": control_results,
        "compliant": sum(1 for c in control_results if c["status"] == "implemented"),
        "partial": sum(1 for c in control_results if c["status"] == "partial"),
        "gaps": sum(1 for c in control_results if c["status"] == "gap")
    }
def calculate_risk_level(overall_score: float, vulnerabilities: List[Dict], phi_data: Dict) -> Dict:
    """Calculate overall HIPAA risk level."""
    # Base risk from compliance score
    if overall_score >= 80:
        base_risk = "LOW"
        base_score = 1
    elif overall_score >= 60:
        base_risk = "MEDIUM"
        base_score = 2
    elif overall_score >= 40:
        base_risk = "HIGH"
        base_score = 3
    else:
        base_risk = "CRITICAL"
        base_score = 4

    # Adjust for vulnerabilities
    critical_vulns = sum(1 for v in vulnerabilities if "password" in v["vulnerability"].lower() or "secret" in v["vulnerability"].lower())
    if critical_vulns > 0:
        base_score = min(4, base_score + 1)

    # Adjust for PHI handling
    if phi_data["phi_detected"] and base_score < 4:
        base_score = min(4, base_score + 0.5)

    # Map back to risk level
    risk_levels = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
    final_risk = risk_levels.get(int(base_score), "HIGH")

    return {
        "risk_level": final_risk,
        "compliance_score": overall_score,
        "vulnerability_count": len(vulnerabilities),
        "phi_handling_detected": phi_data["phi_detected"]
    }
