# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qsr_compliance_checker_base import *  # noqa: F403,E402
# fmt: off
from qsr_compliance_checker_p1 import _mod_cg0_0  # noqa: E402,E501
from qsr_compliance_checker_p2 import _mod_cg0_1  # noqa: E402,E501
# fmt: on


def _mod_cg0_2():
    return {
        "820.100": {
        "title": "Corrective and Preventive Action",
        "subsections": {
            "820.100(a)": {
                "title": "CAPA Procedure",
                "required_evidence": ["capa_procedure", "capa_records"],
                "doc_patterns": ["capa*", "corrective*", "preventive*"],
                "keywords": ["CAPA", "corrective action", "preventive action", "root cause"]
            }
        }
    },
        "820.120": {
        "title": "Device Labeling",
        "subsections": {
            "820.120": {
                "title": "Labeling Controls",
                "required_evidence": ["labeling_procedure", "label_inspection"],
                "doc_patterns": ["label*", "labeling*"],
                "keywords": ["labeling", "label inspection", "UDI"]
            }
        }
    },
        "820.180": {
        "title": "General Requirements - Records",
        "subsections": {
            "820.180": {
                "title": "Records Requirements",
                "required_evidence": ["records_management_procedure", "retention_schedule"],
                "doc_patterns": ["record*", "retention*", "archive*"],
                "keywords": ["records", "retention", "archive", "backup"]
            }
        }
    },
        "820.181": {
        "title": "Device Master Record",
        "subsections": {
            "820.181": {
                "title": "DMR Contents",
                "required_evidence": ["dmr_index", "dmr"],
                "doc_patterns": ["dmr*", "device_master*"],
                "keywords": ["device master record", "DMR", "specifications"]
            }
        }
    },
        "820.184": {
        "title": "Device History Record",
        "subsections": {
            "820.184": {
                "title": "DHR Contents",
                "required_evidence": ["dhr_template", "dhr_records"],
                "doc_patterns": ["dhr*", "device_history*", "batch_record*"],
                "keywords": ["device history record", "DHR", "production record"]
            }
        }
    },
        "820.198": {
        "title": "Complaint Files",
        "subsections": {
            "820.198": {
                "title": "Complaint Handling",
                "required_evidence": ["complaint_procedure", "complaint_records"],
                "doc_patterns": ["complaint*", "customer_feedback*"],
                "keywords": ["complaint", "customer feedback", "MDR"]
            }
        }
    },
    }
QSR_REQUIREMENTS = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2()}
