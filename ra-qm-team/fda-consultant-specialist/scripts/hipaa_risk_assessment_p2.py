# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hipaa_risk_assessment_base import *  # noqa: F403,E402


PHI_PATTERNS = [
    (r"patient.*name", "Patient Name"),
    (r"ssn|social.*security", "Social Security Number"),
    (r"date.*of.*birth|dob", "Date of Birth"),
    (r"medical.*record", "Medical Record Number"),
    (r"health.*plan", "Health Plan ID"),
    (r"diagnosis|icd.*code", "Diagnosis/ICD Code"),
    (r"prescription|medication", "Medication/Prescription"),
    (r"insurance", "Insurance Information"),
    (r"phone.*number|telephone", "Phone Number"),
    (r"email.*address", "Email Address"),
    (r"address|street|city|zip", "Physical Address"),
    (r"biometric", "Biometric Data")
]
VULNERABILITY_PATTERNS = [
    (r"password.*=.*['\"]", "Hardcoded password"),
    (r"api.*key.*=.*['\"]", "Hardcoded API key"),
    (r"secret.*=.*['\"]", "Hardcoded secret"),
    (r"http://(?!localhost)", "Unencrypted HTTP connection"),
    (r"verify.*=.*False", "SSL verification disabled"),
    (r"dynamic.*code.*execution", "Dynamic code execution risk"),
    (r"disable.*ssl", "SSL disabled"),
    (r"insecure", "Insecure configuration")
]
def scan_documentation(project_dir: Path, patterns: List[str]) -> List[str]:
    """Scan for documentation matching patterns."""
    found = []
    doc_dirs = [
        project_dir / "docs",
        project_dir / "documentation",
        project_dir / "policies",
        project_dir / "compliance",
        project_dir / "hipaa",
        project_dir
    ]

    for doc_dir in doc_dirs:
        if not doc_dir.exists():
            continue

        for pattern in patterns:
            for ext in ["*.md", "*.pdf", "*.docx", "*.doc", "*.txt"]:
                try:
                    for match in doc_dir.glob(f"**/{pattern}{ext}"):
                        rel_path = str(match.relative_to(project_dir))
                        if rel_path not in found:
                            found.append(rel_path)
                except Exception:
                    continue

    return found
def scan_code_patterns(project_dir: Path, patterns: List[str]) -> List[Dict]:
    """Scan source code for patterns."""
    matches = []
    code_extensions = ["*.py", "*.js", "*.ts", "*.java", "*.cs", "*.go", "*.rb"]

    src_dirs = [
        project_dir / "src",
        project_dir / "app",
        project_dir / "lib",
        project_dir
    ]

    for src_dir in src_dirs:
        if not src_dir.exists():
            continue

        for ext in code_extensions:
            try:
                for file_path in src_dir.glob(f"**/{ext}"):
                    # Skip node_modules, venv, etc.
                    if any(skip in str(file_path) for skip in ["node_modules", "venv", ".venv", "__pycache__", ".git"]):
                        continue

                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        for pattern in patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                rel_path = str(file_path.relative_to(project_dir))
                                matches.append({
                                    "file": rel_path,
                                    "pattern": pattern
                                })
                                break  # One match per file per control is enough
                    except Exception:
                        continue
            except Exception:
                continue

    return matches
def detect_phi_handling(project_dir: Path) -> Dict:
    """Detect potential PHI handling in code."""
    phi_found = []
    code_extensions = ["*.py", "*.js", "*.ts", "*.java", "*.cs", "*.go"]

    for ext in code_extensions:
        try:
            for file_path in project_dir.glob(f"**/{ext}"):
                if any(skip in str(file_path) for skip in ["node_modules", "venv", ".venv", "__pycache__", ".git"]):
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    rel_path = str(file_path.relative_to(project_dir))

                    for pattern, phi_type in PHI_PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            phi_found.append({
                                "file": rel_path,
                                "phi_type": phi_type
                            })
                            break
                except Exception:
                    continue
        except Exception:
            continue

    return {
        "phi_detected": len(phi_found) > 0,
        "files_with_phi": phi_found,
        "phi_types": list(set(p["phi_type"] for p in phi_found))
    }
