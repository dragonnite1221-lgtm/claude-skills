# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fda_submission_tracker_base import *  # noqa: F403,E402


FDA_TIMELINES = {
    "510k_traditional": {
        "acceptance_review": 15,
        "substantive_review": 90,
        "total_goal": 90,
        "ai_response": 180  # Days to respond to Additional Information
    },
    "510k_special": {
        "acceptance_review": 15,
        "substantive_review": 30,
        "total_goal": 30,
        "ai_response": 180
    },
    "510k_abbreviated": {
        "acceptance_review": 15,
        "substantive_review": 30,
        "total_goal": 30,
        "ai_response": 180
    },
    "de_novo": {
        "acceptance_review": 60,
        "substantive_review": 150,
        "total_goal": 150,
        "ai_response": 180
    },
    "pma": {
        "acceptance_review": 45,
        "substantive_review": 180,
        "total_goal": 180,
        "ai_response": 180
    },
    "pma_supplement": {
        "acceptance_review": 15,
        "substantive_review": 180,
        "total_goal": 180,
        "ai_response": 180
    }
}
MILESTONES = {
    "510k": [
        {"id": "predicate_identified", "name": "Predicate Device Identified", "phase": "planning"},
        {"id": "testing_complete", "name": "Performance Testing Complete", "phase": "preparation"},
        {"id": "documentation_complete", "name": "Submission Documentation Complete", "phase": "preparation"},
        {"id": "submission_sent", "name": "Submission Sent to FDA", "phase": "submission"},
        {"id": "acknowledgment_received", "name": "FDA Acknowledgment Received", "phase": "review"},
        {"id": "acceptance_decision", "name": "Acceptance Review Complete", "phase": "review"},
        {"id": "ai_request", "name": "Additional Information Request", "phase": "review", "optional": True},
        {"id": "ai_response", "name": "AI Response Submitted", "phase": "review", "optional": True},
        {"id": "se_decision", "name": "Substantial Equivalence Decision", "phase": "decision"},
        {"id": "clearance_letter", "name": "510(k) Clearance Letter Received", "phase": "decision"}
    ],
    "de_novo": [
        {"id": "classification_determined", "name": "Classification Determination", "phase": "planning"},
        {"id": "special_controls_defined", "name": "Special Controls Defined", "phase": "preparation"},
        {"id": "risk_assessment_complete", "name": "Risk Assessment Complete", "phase": "preparation"},
        {"id": "testing_complete", "name": "Performance Testing Complete", "phase": "preparation"},
        {"id": "submission_sent", "name": "Submission Sent to FDA", "phase": "submission"},
        {"id": "acknowledgment_received", "name": "FDA Acknowledgment Received", "phase": "review"},
        {"id": "acceptance_decision", "name": "Acceptance Review Complete", "phase": "review"},
        {"id": "ai_request", "name": "Additional Information Request", "phase": "review", "optional": True},
        {"id": "ai_response", "name": "AI Response Submitted", "phase": "review", "optional": True},
        {"id": "classification_decision", "name": "De Novo Classification Decision", "phase": "decision"}
    ],
    "pma": [
        {"id": "ide_approved", "name": "IDE Approval (if required)", "phase": "planning", "optional": True},
        {"id": "clinical_complete", "name": "Clinical Study Complete", "phase": "preparation"},
        {"id": "clinical_report_complete", "name": "Clinical Study Report Complete", "phase": "preparation"},
        {"id": "documentation_complete", "name": "PMA Documentation Complete", "phase": "preparation"},
        {"id": "submission_sent", "name": "PMA Submission Sent to FDA", "phase": "submission"},
        {"id": "acknowledgment_received", "name": "FDA Acknowledgment Received", "phase": "review"},
        {"id": "filing_decision", "name": "Filing Decision", "phase": "review"},
        {"id": "ai_request", "name": "Major Deficiency Letter", "phase": "review", "optional": True},
        {"id": "ai_response", "name": "Deficiency Response Submitted", "phase": "review", "optional": True},
        {"id": "panel_meeting", "name": "Advisory Committee Meeting", "phase": "review", "optional": True},
        {"id": "approval_decision", "name": "PMA Approval Decision", "phase": "decision"}
    ]
}
def find_submission_config(project_dir: Path) -> Optional[Dict]:
    """Find and load submission configuration file."""
    config_paths = [
        project_dir / "fda_submission.json",
        project_dir / "regulatory" / "fda_submission.json",
        project_dir / ".fda" / "submission.json"
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                continue

    return None
