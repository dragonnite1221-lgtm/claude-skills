# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402


def _mod_cg0_3():
    return {
        "7.5.5": {
        "title": "Sterile Medical Devices",
        "questions": [
            "Is sterilization validated?",
            "Are process parameters controlled?",
            "Is sterile barrier validated?",
            "Are sterilization records maintained?"
        ]
    },
        "7.5.6": {
        "title": "Validation of Processes",
        "questions": [
            "Are special processes identified?",
            "Are validation procedures documented?",
            "Is equipment qualified?",
            "Are personnel qualified?",
            "Are validation records maintained?",
            "Are revalidation criteria defined?"
        ]
    },
        "7.5.7": {
        "title": "Particular Requirements for Validation",
        "questions": [
            "Are validation methods defined?",
            "Are acceptance criteria established?",
            "Is software validation appropriate?",
            "Are validation records maintained?"
        ]
    },
        "7.5.8": {
        "title": "Identification",
        "questions": [
            "Is product identified throughout realization?",
            "Is documentation identified?",
            "Is UDI implemented as required?"
        ]
    },
        "7.5.9": {
        "title": "Traceability",
        "questions": [
            "Are traceability procedures documented?",
            "Are components traceable?",
            "Is work environment recorded?",
            "Is distribution recorded?",
            "Is traceability extent defined?"
        ]
    },
        "7.5.10": {
        "title": "Customer Property",
        "questions": [
            "Is customer property identified?",
            "Is it verified on receipt?",
            "Is it protected and safeguarded?",
            "Is loss or damage reported?"
        ]
    },
        "7.5.11": {
        "title": "Preservation of Product",
        "questions": [
            "Is product identified?",
            "Is handling controlled?",
            "Is packaging controlled?",
            "Is storage controlled?",
            "Is protection adequate?"
        ]
    },
        "7.6": {
        "title": "Control of Monitoring and Measuring Equipment",
        "questions": [
            "Is equipment calibrated?",
            "Is calibration traceable?",
            "Is calibration status identified?",
            "Is equipment protected from damage?",
            "Is software validated?",
            "Are records maintained?"
        ]
    },
        "8.1": {
        "title": "Measurement, Analysis and Improvement - General",
        "questions": [
            "Are monitoring activities planned?",
            "Are analysis activities planned?",
            "Are improvement activities planned?"
        ]
    },
        "8.2.1": {
        "title": "Feedback",
        "questions": [
            "Is feedback collected?",
            "Is feedback analyzed?",
            "Is feedback used for improvement?",
            "Is regulatory feedback included?"
        ]
    },
        "8.2.2": {
        "title": "Complaint Handling",
        "questions": [
            "Is there a complaint procedure?",
            "Are complaints investigated?",
            "Are regulatory reports made if required?",
            "Is trend analysis performed?",
            "Are CAPAs initiated when warranted?"
        ]
    },
        "8.2.3": {
        "title": "Reporting to Regulatory Authorities",
        "questions": [
            "Are reporting requirements identified?",
            "Are reports submitted timely?",
            "Are records maintained?"
        ]
    },
    }
