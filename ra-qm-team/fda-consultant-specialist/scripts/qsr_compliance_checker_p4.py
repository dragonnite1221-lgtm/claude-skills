# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qsr_compliance_checker_base import *  # noqa: F403,E402


def search_documentation(project_dir: Path, patterns: List[str], keywords: List[str]) -> Dict:
    """Search for documentation matching patterns and keywords."""
    result = {
        "documents_found": [],
        "keyword_matches": [],
        "evidence_strength": "none"
    }

    # Common documentation directories
    doc_dirs = [
        project_dir / "qms",
        project_dir / "quality",
        project_dir / "docs",
        project_dir / "documentation",
        project_dir / "procedures",
        project_dir / "sops",
        project_dir / "dhf",
        project_dir / "dmr",
        project_dir
    ]

    # Search for document patterns
    for doc_dir in doc_dirs:
        if not doc_dir.exists():
            continue

        for pattern in patterns:
            for ext in ["*.md", "*.pdf", "*.docx", "*.doc", "*.txt"]:
                full_pattern = f"**/{pattern}{ext}" if not pattern.endswith("*") else f"**/{pattern[:-1]}{ext}"
                try:
                    matches = list(doc_dir.glob(full_pattern))
                    for match in matches:
                        rel_path = str(match.relative_to(project_dir))
                        if rel_path not in result["documents_found"]:
                            result["documents_found"].append(rel_path)
                except Exception:
                    continue

    # Search for keywords in markdown and text files
    for doc_dir in doc_dirs:
        if not doc_dir.exists():
            continue

        for ext in ["*.md", "*.txt"]:
            try:
                for file_path in doc_dir.glob(f"**/{ext}"):
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                rel_path = str(file_path.relative_to(project_dir))
                                if rel_path not in result["keyword_matches"]:
                                    result["keyword_matches"].append(rel_path)
                    except Exception:
                        continue
            except Exception:
                continue

    # Determine evidence strength
    if result["documents_found"] and result["keyword_matches"]:
        result["evidence_strength"] = "strong"
    elif result["documents_found"] or result["keyword_matches"]:
        result["evidence_strength"] = "partial"
    else:
        result["evidence_strength"] = "none"

    return result
def assess_section(project_dir: Path, section_id: str, section_data: Dict) -> Dict:
    """Assess compliance for a QSR section."""
    result = {
        "section": section_id,
        "title": section_data["title"],
        "subsections": [],
        "compliance_score": 0,
        "total_subsections": len(section_data["subsections"]),
        "compliant_subsections": 0
    }

    for subsection_id, subsection_data in section_data["subsections"].items():
        evidence = search_documentation(
            project_dir,
            subsection_data["doc_patterns"],
            subsection_data["keywords"]
        )

        subsection_result = {
            "subsection": subsection_id,
            "title": subsection_data["title"],
            "required_evidence": subsection_data["required_evidence"],
            "evidence_found": evidence,
            "status": "gap" if evidence["evidence_strength"] == "none" else (
                "partial" if evidence["evidence_strength"] == "partial" else "compliant"
            )
        }

        if subsection_result["status"] == "compliant":
            result["compliant_subsections"] += 1
        elif subsection_result["status"] == "partial":
            result["compliant_subsections"] += 0.5

        result["subsections"].append(subsection_result)

    if result["total_subsections"] > 0:
        result["compliance_score"] = round(
            (result["compliant_subsections"] / result["total_subsections"]) * 100, 1
        )

    return result
