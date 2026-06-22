# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qsr_compliance_checker_base import *  # noqa: F403,E402


def _mod_cg0_1():
    return {
        "820.70": {
        "title": "Production and Process Controls",
        "subsections": {
            "820.70(a)": {
                "title": "General Process Controls",
                "required_evidence": ["manufacturing_procedures", "work_instructions"],
                "doc_patterns": ["manufacturing*", "production*", "work_instruction*", "wi_*"],
                "keywords": ["manufacturing process", "production", "process parameters"]
            },
            "820.70(b)": {
                "title": "Production and Process Changes",
                "required_evidence": ["process_change_procedure"],
                "doc_patterns": ["process_change*", "manufacturing_change*"],
                "keywords": ["process change", "production change", "change control"]
            },
            "820.70(c)": {
                "title": "Environmental Control",
                "required_evidence": ["environmental_control_procedure", "monitoring_records"],
                "doc_patterns": ["environmental*", "cleanroom*", "env_monitoring*"],
                "keywords": ["environmental control", "cleanroom", "contamination"]
            },
            "820.70(d)": {
                "title": "Personnel",
                "required_evidence": ["training_procedure", "training_records"],
                "doc_patterns": ["training*", "personnel*", "competency*"],
                "keywords": ["training", "personnel qualification", "competency"]
            },
            "820.70(e)": {
                "title": "Contamination Control",
                "required_evidence": ["contamination_control_procedure"],
                "doc_patterns": ["contamination*", "cleaning*", "hygiene*"],
                "keywords": ["contamination", "cleaning", "hygiene"]
            },
            "820.70(f)": {
                "title": "Buildings",
                "required_evidence": ["facility_requirements"],
                "doc_patterns": ["facility*", "building*"],
                "keywords": ["facility", "buildings", "manufacturing area"]
            },
            "820.70(g)": {
                "title": "Equipment",
                "required_evidence": ["equipment_maintenance_procedure", "maintenance_records"],
                "doc_patterns": ["equipment*", "maintenance*", "preventive_maintenance*"],
                "keywords": ["equipment", "maintenance", "calibration"]
            },
            "820.70(h)": {
                "title": "Manufacturing Material",
                "required_evidence": ["material_handling_procedure"],
                "doc_patterns": ["material*", "handling*", "storage*"],
                "keywords": ["manufacturing material", "handling", "storage"]
            },
            "820.70(i)": {
                "title": "Automated Processes",
                "required_evidence": ["software_validation", "automated_process_validation"],
                "doc_patterns": ["software_val*", "csv*", "automation*"],
                "keywords": ["software validation", "automated", "computer system"]
            }
        }
    },
        "820.72": {
        "title": "Inspection, Measuring, and Test Equipment",
        "subsections": {
            "820.72(a)": {
                "title": "Calibration",
                "required_evidence": ["calibration_procedure", "calibration_records"],
                "doc_patterns": ["calibration*", "cal_*"],
                "keywords": ["calibration", "accuracy", "measurement"]
            },
            "820.72(b)": {
                "title": "Calibration Standards",
                "required_evidence": ["calibration_standards", "traceability_records"],
                "doc_patterns": ["calibration_standard*", "nist*", "traceability*"],
                "keywords": ["calibration standards", "NIST", "traceability"]
            }
        }
    },
        "820.75": {
        "title": "Process Validation",
        "subsections": {
            "820.75(a)": {
                "title": "Process Validation Requirements",
                "required_evidence": ["process_validation_procedure", "validation_protocols"],
                "doc_patterns": ["process_validation*", "pv_*", "validation_protocol*"],
                "keywords": ["process validation", "IQ", "OQ", "PQ"]
            },
            "820.75(b)": {
                "title": "Validation Monitoring",
                "required_evidence": ["validation_monitoring", "revalidation_criteria"],
                "doc_patterns": ["revalidation*", "validation_monitoring*"],
                "keywords": ["monitoring", "revalidation", "process performance"]
            }
        }
    },
        "820.90": {
        "title": "Nonconforming Product",
        "subsections": {
            "820.90(a)": {
                "title": "Nonconforming Product Control",
                "required_evidence": ["ncr_procedure", "nonconforming_records"],
                "doc_patterns": ["ncr*", "nonconform*", "nc_*"],
                "keywords": ["nonconforming", "NCR", "disposition"]
            },
            "820.90(b)": {
                "title": "Nonconformance Review",
                "required_evidence": ["ncr_review_procedure"],
                "doc_patterns": ["ncr_review*", "mrb*"],
                "keywords": ["review", "disposition", "concession"]
            }
        }
    },
    }
