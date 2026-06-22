# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402


def _mod_cg0_1():
    return {
        "5.5.2": {
        "title": "Management Representative",
        "questions": [
            "Is a management representative appointed?",
            "Is authority to ensure QMS processes established?",
            "Is authority to report to top management defined?",
            "Is authority to promote awareness of requirements defined?"
        ]
    },
        "5.5.3": {
        "title": "Internal Communication",
        "questions": [
            "Are communication processes established?",
            "Is QMS effectiveness communicated?",
            "Is information communicated appropriately?"
        ]
    },
        "5.6": {
        "title": "Management Review",
        "questions": [
            "Are management reviews planned?",
            "Are all required inputs reviewed?",
            "Are outputs documented?",
            "Are action items followed up?",
            "Are records maintained?"
        ]
    },
        "6.1": {
        "title": "Provision of Resources",
        "questions": [
            "Are resources determined?",
            "Are resources provided for QMS?",
            "Are resources provided for customer satisfaction?",
            "Are resources provided for regulatory compliance?"
        ]
    },
        "6.2": {
        "title": "Human Resources",
        "questions": [
            "Is competence defined for personnel?",
            "Is training provided to achieve competence?",
            "Is training effectiveness evaluated?",
            "Is awareness of job relevance ensured?",
            "Are training records maintained?"
        ]
    },
        "6.3": {
        "title": "Infrastructure",
        "questions": [
            "Is necessary infrastructure determined?",
            "Are buildings and workspace adequate?",
            "Is process equipment adequate?",
            "Are supporting services adequate?",
            "Are maintenance requirements documented?"
        ]
    },
        "6.4": {
        "title": "Work Environment",
        "questions": [
            "Is work environment determined?",
            "Are environmental requirements documented?",
            "Is contamination control adequate?",
            "Are personnel health and cleanliness controlled?",
            "Are environmental conditions monitored?"
        ]
    },
        "7.1": {
        "title": "Planning of Product Realization",
        "questions": [
            "Are quality objectives for product defined?",
            "Are processes needed determined?",
            "Is verification and validation defined?",
            "Are records requirements defined?",
            "Is risk management applied?"
        ]
    },
        "7.2": {
        "title": "Customer-Related Processes",
        "questions": [
            "Are customer requirements determined?",
            "Are regulatory requirements determined?",
            "Are requirements reviewed before commitment?",
            "Are differences resolved before acceptance?",
            "Is communication with customers effective?"
        ]
    },
        "7.3.1": {
        "title": "Design and Development Planning",
        "questions": [
            "Are design stages determined?",
            "Are review activities defined?",
            "Are verification activities defined?",
            "Are validation activities defined?",
            "Are responsibilities assigned?",
            "Are interfaces managed?"
        ]
    },
        "7.3.2": {
        "title": "Design and Development Inputs",
        "questions": [
            "Are functional requirements defined?",
            "Are performance requirements defined?",
            "Are safety requirements defined?",
            "Are regulatory requirements identified?",
            "Are previous design inputs considered?",
            "Are risk management outputs included?"
        ]
    },
        "7.3.3": {
        "title": "Design and Development Outputs",
        "questions": [
            "Do outputs meet input requirements?",
            "Is purchasing information provided?",
            "Are acceptance criteria defined?",
            "Are essential characteristics specified?",
            "Are outputs approved before release?"
        ]
    },
    }
