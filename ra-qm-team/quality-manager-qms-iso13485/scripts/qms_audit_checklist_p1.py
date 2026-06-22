# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402


def _mod_cg0_0():
    return {
        "4.1": {
        "title": "General Requirements",
        "questions": [
            "Are QMS processes identified and documented?",
            "Is the sequence and interaction of processes defined?",
            "Are criteria and methods for process operation determined?",
            "Are resources and information available for process operation?",
            "Are processes monitored, measured, and analyzed?",
            "Are actions taken to achieve planned results?",
            "Is outsourced process control documented?",
            "Are changes to processes managed?"
        ]
    },
        "4.2.1": {
        "title": "Documentation Requirements - General",
        "questions": [
            "Is a quality policy documented?",
            "Are quality objectives documented?",
            "Is a quality manual maintained?",
            "Are required documented procedures established?",
            "Are documents needed for process planning and operation maintained?",
            "Are required records maintained?",
            "Is a medical device file established for each device type?"
        ]
    },
        "4.2.2": {
        "title": "Quality Manual",
        "questions": [
            "Does the quality manual include QMS scope?",
            "Are exclusions justified?",
            "Are documented procedures included or referenced?",
            "Is the interaction between processes described?",
            "Is the quality manual controlled?"
        ]
    },
        "4.2.3": {
        "title": "Control of Documents",
        "questions": [
            "Are documents approved before issue?",
            "Are documents reviewed and updated as necessary?",
            "Are changes and revision status identified?",
            "Are current versions available at points of use?",
            "Are documents legible and identifiable?",
            "Are external documents identified and controlled?",
            "Is unintended use of obsolete documents prevented?",
            "Is there a document change control process?"
        ]
    },
        "4.2.4": {
        "title": "Control of Records",
        "questions": [
            "Is there a procedure for record control?",
            "Are records legible and identifiable?",
            "Are records retrievable?",
            "Are retention times defined?",
            "Is protection from damage ensured?",
            "Are confidential records protected?",
            "Is record disposal controlled?"
        ]
    },
        "5.1": {
        "title": "Management Commitment",
        "questions": [
            "Is there evidence of management commitment to QMS?",
            "Is the importance of regulatory requirements communicated?",
            "Is a quality policy established?",
            "Are quality objectives established?",
            "Are management reviews conducted?",
            "Are resources provided for QMS?"
        ]
    },
        "5.2": {
        "title": "Customer Focus",
        "questions": [
            "Are customer requirements determined?",
            "Are applicable regulatory requirements determined?",
            "Are customer and regulatory requirements met?",
            "Is customer satisfaction enhanced?"
        ]
    },
        "5.3": {
        "title": "Quality Policy",
        "questions": [
            "Is the quality policy appropriate to the organization?",
            "Does it include commitment to compliance?",
            "Does it include commitment to effectiveness?",
            "Does it provide framework for quality objectives?",
            "Is it communicated and understood?",
            "Is it reviewed for continuing suitability?"
        ]
    },
        "5.4.1": {
        "title": "Quality Objectives",
        "questions": [
            "Are quality objectives measurable?",
            "Are they consistent with quality policy?",
            "Are they established at relevant functions?",
            "Do they include product requirements?",
            "Do they include compliance requirements?"
        ]
    },
        "5.4.2": {
        "title": "QMS Planning",
        "questions": [
            "Is QMS planning carried out to meet requirements?",
            "Is QMS planning done to meet quality objectives?",
            "Is QMS integrity maintained during changes?"
        ]
    },
        "5.5.1": {
        "title": "Responsibility and Authority",
        "questions": [
            "Are responsibilities and authorities defined?",
            "Are they documented?",
            "Are they communicated?",
            "Are interrelationships defined?"
        ]
    },
    }
