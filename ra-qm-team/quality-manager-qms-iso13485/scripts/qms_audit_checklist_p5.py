# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402
# fmt: off
from qms_audit_checklist_p1 import _mod_cg0_0  # noqa: E402,E501
from qms_audit_checklist_p2 import _mod_cg0_1  # noqa: E402,E501
from qms_audit_checklist_p3 import _mod_cg0_2  # noqa: E402,E501
from qms_audit_checklist_p4 import _mod_cg0_3  # noqa: E402,E501
# fmt: on


def _mod_cg0_4():
    return {
        "8.2.4": {
        "title": "Internal Audit",
        "questions": [
            "Is an audit program established?",
            "Are audit criteria defined?",
            "Are auditors independent?",
            "Are auditors competent?",
            "Are audit records maintained?",
            "Are findings followed up?"
        ]
    },
        "8.2.5": {
        "title": "Monitoring and Measurement of Processes",
        "questions": [
            "Are processes monitored?",
            "Are suitable methods used?",
            "Is process capability demonstrated?",
            "Are corrections made when needed?"
        ]
    },
        "8.2.6": {
        "title": "Monitoring and Measurement of Product",
        "questions": [
            "Is product inspected?",
            "Are acceptance criteria met?",
            "Is release authorized?",
            "Is traceability to inspection recorded?",
            "Are records maintained?"
        ]
    },
        "8.3": {
        "title": "Control of Nonconforming Product",
        "questions": [
            "Is nonconforming product identified?",
            "Is it documented?",
            "Is it evaluated?",
            "Is it segregated?",
            "Is disposition determined?",
            "Is rework verified?",
            "Is concession controlled?",
            "Is post-delivery NC investigated?"
        ]
    },
        "8.4": {
        "title": "Analysis of Data",
        "questions": [
            "Is data collected?",
            "Is feedback analyzed?",
            "Is conformity data analyzed?",
            "Is process data analyzed?",
            "Is supplier data analyzed?",
            "Are audit results analyzed?"
        ]
    },
        "8.5.1": {
        "title": "Improvement - General",
        "questions": [
            "Is continual improvement pursued?",
            "Are policy, objectives, audits, data, actions, and reviews used?"
        ]
    },
        "8.5.2": {
        "title": "Corrective Action",
        "questions": [
            "Is there a CA procedure?",
            "Are NCs reviewed (including complaints)?",
            "Is root cause determined?",
            "Is action needed evaluated?",
            "Is action determined and implemented?",
            "Are results documented?",
            "Is effectiveness verified?"
        ]
    },
        "8.5.3": {
        "title": "Preventive Action",
        "questions": [
            "Is there a PA procedure?",
            "Are potential NCs identified?",
            "Is action needed evaluated?",
            "Is action determined and implemented?",
            "Are results documented?",
            "Is effectiveness verified?"
        ]
    },
    }
ISO13485_CLAUSES = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2(), **_mod_cg0_3(), **_mod_cg0_4()}
PROCESS_MAPPING = {
    "document-control": ["4.2.1", "4.2.2", "4.2.3", "4.2.4"],
    "management-review": ["5.6"],
    "internal-audit": ["8.2.4"],
    "training": ["6.2"],
    "design-control": ["7.3.1", "7.3.2", "7.3.3", "7.3.4", "7.3.5", "7.3.6", "7.3.7", "7.3.8"],
    "purchasing": ["7.4.1", "7.4.2", "7.4.3"],
    "production": ["7.5.1", "7.5.2", "7.5.6", "7.5.7", "7.5.8", "7.5.9", "7.5.11"],
    "capa": ["8.5.2", "8.5.3"],
    "nonconformity": ["8.3"],
    "calibration": ["7.6"],
    "complaint-handling": ["8.2.1", "8.2.2", "8.2.3"],
    "risk-management": ["7.1"],
    "infrastructure": ["6.3", "6.4"],
    "customer-requirements": ["5.2", "7.2"]
}
def get_clause_checklist(clause: str) -> dict:
    """Get audit checklist for a specific clause."""
    if clause not in ISO13485_CLAUSES:
        return {"error": f"Clause {clause} not found"}

    clause_data = ISO13485_CLAUSES[clause]
    return {
        "clause": clause,
        "title": clause_data["title"],
        "questions": clause_data["questions"],
        "question_count": len(clause_data["questions"])
    }
