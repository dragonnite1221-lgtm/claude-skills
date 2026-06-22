# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qsr_compliance_checker_base import *  # noqa: F403,E402


def _mod_cg0_0():
    return {
        "820.20": {
        "title": "Management Responsibility",
        "subsections": {
            "820.20(a)": {
                "title": "Quality Policy",
                "required_evidence": ["quality_policy", "quality_manual", "quality_objectives"],
                "doc_patterns": ["quality_policy*", "quality_manual*", "qms_manual*"],
                "keywords": ["quality policy", "quality objectives", "management commitment"]
            },
            "820.20(b)": {
                "title": "Organization",
                "required_evidence": ["org_chart", "job_descriptions", "authority_matrix"],
                "doc_patterns": ["org_chart*", "organization*", "job_desc*", "authority*"],
                "keywords": ["organizational structure", "responsibility", "authority"]
            },
            "820.20(c)": {
                "title": "Management Review",
                "required_evidence": ["management_review_procedure", "management_review_records"],
                "doc_patterns": ["management_review*", "mgmt_review*", "qmr*"],
                "keywords": ["management review", "review meeting", "quality system effectiveness"]
            }
        }
    },
        "820.30": {
        "title": "Design Controls",
        "subsections": {
            "820.30(a)": {
                "title": "Design and Development Planning",
                "required_evidence": ["design_plan", "development_plan"],
                "doc_patterns": ["design_plan*", "dev_plan*", "development_plan*"],
                "keywords": ["design planning", "development phases", "design milestones"]
            },
            "820.30(b)": {
                "title": "Design Input",
                "required_evidence": ["design_input", "requirements_specification"],
                "doc_patterns": ["design_input*", "requirement*", "srs*", "prs*"],
                "keywords": ["design input", "requirements", "user needs", "intended use"]
            },
            "820.30(c)": {
                "title": "Design Output",
                "required_evidence": ["design_output", "specifications", "drawings"],
                "doc_patterns": ["design_output*", "specification*", "drawing*", "bom*"],
                "keywords": ["design output", "specifications", "acceptance criteria"]
            },
            "820.30(d)": {
                "title": "Design Review",
                "required_evidence": ["design_review_procedure", "design_review_records"],
                "doc_patterns": ["design_review*", "dr_record*", "dr_minutes*"],
                "keywords": ["design review", "review meeting", "design evaluation"]
            },
            "820.30(e)": {
                "title": "Design Verification",
                "required_evidence": ["verification_plan", "verification_results"],
                "doc_patterns": ["verification*", "test_report*", "dv_*"],
                "keywords": ["verification", "testing", "design verification"]
            },
            "820.30(f)": {
                "title": "Design Validation",
                "required_evidence": ["validation_plan", "validation_results"],
                "doc_patterns": ["validation*", "clinical*", "usability*", "val_*"],
                "keywords": ["validation", "user needs", "intended use", "clinical evaluation"]
            },
            "820.30(g)": {
                "title": "Design Transfer",
                "required_evidence": ["transfer_checklist", "transfer_verification"],
                "doc_patterns": ["transfer*", "production_release*"],
                "keywords": ["design transfer", "manufacturing", "production"]
            },
            "820.30(h)": {
                "title": "Design Changes",
                "required_evidence": ["change_control_procedure", "change_records"],
                "doc_patterns": ["change_control*", "ecn*", "eco*", "dcr*"],
                "keywords": ["design change", "change control", "modification"]
            },
            "820.30(i)": {
                "title": "Design History File",
                "required_evidence": ["dhf_index", "dhf"],
                "doc_patterns": ["dhf*", "design_history*"],
                "keywords": ["design history file", "DHF", "design records"]
            }
        }
    },
        "820.40": {
        "title": "Document Controls",
        "subsections": {
            "820.40(a)": {
                "title": "Document Approval and Distribution",
                "required_evidence": ["document_control_procedure"],
                "doc_patterns": ["document_control*", "doc_control*", "sop_document*"],
                "keywords": ["document approval", "document distribution", "controlled documents"]
            },
            "820.40(b)": {
                "title": "Document Changes",
                "required_evidence": ["document_change_procedure", "revision_history"],
                "doc_patterns": ["revision_history*", "document_change*"],
                "keywords": ["document change", "revision", "document modification"]
            }
        }
    },
        "820.50": {
        "title": "Purchasing Controls",
        "subsections": {
            "820.50(a)": {
                "title": "Evaluation of Suppliers",
                "required_evidence": ["supplier_qualification_procedure", "approved_supplier_list"],
                "doc_patterns": ["supplier*", "asl*", "vendor*"],
                "keywords": ["supplier evaluation", "approved supplier", "vendor qualification"]
            },
            "820.50(b)": {
                "title": "Purchasing Data",
                "required_evidence": ["purchasing_procedure", "purchase_order_requirements"],
                "doc_patterns": ["purchas*", "procurement*"],
                "keywords": ["purchasing data", "specifications", "quality requirements"]
            }
        }
    },
    }
