# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402


def _mod_cg0_2():
    return {
        "7.3.4": {
        "title": "Design and Development Review",
        "questions": [
            "Are design reviews conducted at suitable stages?",
            "Is ability to meet requirements evaluated?",
            "Are problems identified?",
            "Are follow-up actions recorded?",
            "Are appropriate functions represented?"
        ]
    },
        "7.3.5": {
        "title": "Design and Development Verification",
        "questions": [
            "Is verification performed per plan?",
            "Do outputs meet inputs?",
            "Are verification records maintained?",
            "Are verification methods appropriate?"
        ]
    },
        "7.3.6": {
        "title": "Design and Development Validation",
        "questions": [
            "Is validation performed per plan?",
            "Is product evaluated for intended use?",
            "Is clinical evaluation included?",
            "Are validation records maintained?",
            "Is validation completed before product delivery?"
        ]
    },
        "7.3.7": {
        "title": "Design and Development Transfer",
        "questions": [
            "Are outputs verified before transfer?",
            "Is manufacturing capability verified?",
            "Are transfer activities documented?"
        ]
    },
        "7.3.8": {
        "title": "Control of Design and Development Changes",
        "questions": [
            "Are design changes identified?",
            "Are changes reviewed?",
            "Are changes verified?",
            "Are changes validated as appropriate?",
            "Is impact on product assessed?",
            "Are changes approved before implementation?"
        ]
    },
        "7.4.1": {
        "title": "Purchasing Process",
        "questions": [
            "Are suppliers evaluated and selected?",
            "Are evaluation criteria established?",
            "Is supplier performance monitored?",
            "Are re-evaluation criteria defined?",
            "Is purchased product verified?"
        ]
    },
        "7.4.2": {
        "title": "Purchasing Information",
        "questions": [
            "Is purchasing information adequate?",
            "Are product requirements specified?",
            "Are QMS requirements specified?",
            "Are personnel requirements specified?"
        ]
    },
        "7.4.3": {
        "title": "Verification of Purchased Product",
        "questions": [
            "Is incoming inspection adequate?",
            "Are verification activities defined?",
            "Are verification records maintained?",
            "Is source verification defined if applicable?"
        ]
    },
        "7.5.1": {
        "title": "Control of Production and Service Provision",
        "questions": [
            "Is product information available?",
            "Are work instructions available?",
            "Is suitable equipment used?",
            "Are monitoring devices available?",
            "Is monitoring implemented?",
            "Are release activities defined?",
            "Are labeling requirements met?"
        ]
    },
        "7.5.2": {
        "title": "Cleanliness of Product",
        "questions": [
            "Are cleanliness requirements documented?",
            "Is contamination controlled?",
            "Are process agents controlled?"
        ]
    },
        "7.5.3": {
        "title": "Installation Activities",
        "questions": [
            "Are installation requirements documented?",
            "Are acceptance criteria defined?",
            "Are installation records maintained?"
        ]
    },
        "7.5.4": {
        "title": "Servicing Activities",
        "questions": [
            "Are servicing procedures documented?",
            "Are reference materials controlled?",
            "Are service records maintained?",
            "Is feedback analyzed?"
        ]
    },
    }
