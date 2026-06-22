# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dpia_generator_base import *  # noqa: F403,E402


LEGAL_BASES = {
    "consent": {
        "article": "Art. 6(1)(a)",
        "description": "Data subject has given consent",
        "requirements": [
            "Consent must be freely given",
            "Specific to the purpose",
            "Informed consent with clear information",
            "Unambiguous indication of wishes",
            "Easy to withdraw"
        ]
    },
    "contract": {
        "article": "Art. 6(1)(b)",
        "description": "Processing necessary for contract performance",
        "requirements": [
            "Contract must exist or be in negotiation",
            "Processing must be necessary for the contract",
            "Cannot process more than contractually needed"
        ]
    },
    "legal_obligation": {
        "article": "Art. 6(1)(c)",
        "description": "Processing necessary for legal obligation",
        "requirements": [
            "Legal obligation must be binding",
            "Must be EU or Member State law",
            "Processing must be necessary to comply"
        ]
    },
    "vital_interests": {
        "article": "Art. 6(1)(d)",
        "description": "Processing necessary to protect vital interests",
        "requirements": [
            "Life-threatening situation",
            "No other legal basis available",
            "Typically emergency situations"
        ]
    },
    "public_interest": {
        "article": "Art. 6(1)(e)",
        "description": "Processing necessary for public interest task",
        "requirements": [
            "Task in public interest or official authority",
            "Legal basis in EU or Member State law",
            "Processing must be necessary"
        ]
    },
    "legitimate_interests": {
        "article": "Art. 6(1)(f)",
        "description": "Processing necessary for legitimate interests",
        "requirements": [
            "Identify the legitimate interest",
            "Show processing is necessary",
            "Balance against data subject rights",
            "Not available for public authorities"
        ]
    }
}
def get_template() -> Dict:
    """Return a blank DPIA input template."""
    return {
        "project_name": "",
        "version": "1.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "controller": {
            "name": "",
            "contact": "",
            "dpo_contact": ""
        },
        "processing_activity": {
            "description": "",
            "purposes": [],
            "legal_basis": "",
            "legal_basis_justification": ""
        },
        "data_subjects": {
            "categories": [],
            "estimated_number": "",
            "vulnerable_groups": False,
            "vulnerable_groups_details": ""
        },
        "personal_data": {
            "categories": [],
            "special_categories": [],
            "source": "",
            "retention_period": ""
        },
        "processing_operations": {
            "collection_method": "",
            "storage_location": "",
            "access_controls": "",
            "automated_decisions": False,
            "profiling": False
        },
        "data_recipients": {
            "internal": [],
            "external_processors": [],
            "third_countries": []
        },
        "dpia_triggers": [],
        "identified_risks": [],
        "mitigations_planned": []
    }
