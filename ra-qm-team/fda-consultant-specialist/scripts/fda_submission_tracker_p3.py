# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fda_submission_tracker_base import *  # noqa: F403,E402


def calculate_submission_readiness(project_dir: Path, submission_type: str) -> Dict:
    """Check submission readiness by looking for required documentation."""

    required_docs = {
        "510k": [
            {"name": "Device Description", "patterns": ["device_description*", "device_desc*"]},
            {"name": "Indications for Use", "patterns": ["indications*", "ifu*"]},
            {"name": "Substantial Equivalence", "patterns": ["substantial_equiv*", "se_comparison*", "predicate*"]},
            {"name": "Performance Testing", "patterns": ["performance*", "test_report*", "bench_test*"]},
            {"name": "Biocompatibility", "patterns": ["biocompat*", "iso_10993*"]},
            {"name": "Labeling", "patterns": ["label*", "ifu*", "instructions*"]},
            {"name": "Software Documentation", "patterns": ["software*", "iec_62304*"], "optional": True},
            {"name": "Sterilization Validation", "patterns": ["steriliz*", "sterility*"], "optional": True}
        ],
        "de_novo": [
            {"name": "Device Description", "patterns": ["device_description*", "device_desc*"]},
            {"name": "Risk Assessment", "patterns": ["risk*", "hazard*"]},
            {"name": "Special Controls", "patterns": ["special_control*"]},
            {"name": "Performance Testing", "patterns": ["performance*", "test_report*"]},
            {"name": "Labeling", "patterns": ["label*", "ifu*"]}
        ],
        "pma": [
            {"name": "Device Description", "patterns": ["device_description*"]},
            {"name": "Manufacturing Information", "patterns": ["manufacturing*", "production*"]},
            {"name": "Clinical Study Report", "patterns": ["clinical*", "csr*"]},
            {"name": "Nonclinical Testing", "patterns": ["nonclinical*", "bench*", "preclinical*"]},
            {"name": "Risk Analysis", "patterns": ["risk*", "fmea*"]},
            {"name": "Labeling", "patterns": ["label*", "ifu*"]}
        ]
    }

    docs_to_check = required_docs.get(submission_type.split("_")[0], required_docs["510k"])

    # Search common documentation directories
    doc_dirs = [
        project_dir / "regulatory",
        project_dir / "regulatory" / "fda",
        project_dir / "docs",
        project_dir / "documentation",
        project_dir / "dhf",
        project_dir
    ]

    results = []
    for doc in docs_to_check:
        found = False
        found_path = None

        for doc_dir in doc_dirs:
            if not doc_dir.exists():
                continue

            for pattern in doc["patterns"]:
                matches = list(doc_dir.glob(f"**/{pattern}"))
                matches.extend(list(doc_dir.glob(f"**/{pattern.upper()}")))
                if matches:
                    found = True
                    found_path = str(matches[0].relative_to(project_dir))
                    break

            if found:
                break

        results.append({
            "name": doc["name"],
            "required": not doc.get("optional", False),
            "found": found,
            "path": found_path
        })

    required_found = sum(1 for r in results if r["required"] and r["found"])
    required_total = sum(1 for r in results if r["required"])

    return {
        "documents": results,
        "required_complete": required_found,
        "required_total": required_total,
        "readiness_percentage": round((required_found / required_total) * 100, 1) if required_total > 0 else 0
    }
def generate_sample_config() -> Dict:
    """Generate sample submission configuration."""
    return {
        "submission_type": "510k_traditional",
        "device_name": "Example Medical Device",
        "product_code": "ABC",
        "predicate_device": {
            "name": "Predicate Device Name",
            "k_number": "K123456"
        },
        "milestones": {
            "predicate_identified": "2024-01-15",
            "testing_complete": "2024-03-01",
            "documentation_complete": "2024-03-15"
        },
        "contacts": {
            "regulatory_lead": "Name",
            "quality_lead": "Name"
        },
        "notes": "Add milestone dates as they are completed"
    }
