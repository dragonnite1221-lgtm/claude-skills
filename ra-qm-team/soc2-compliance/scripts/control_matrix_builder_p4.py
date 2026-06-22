# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from control_matrix_builder_base import *  # noqa: F403,E402


def _mod_cg0_2():
    return {
        "confidentiality": {
        "name": "Confidentiality",
        "controls": [
            {
                "id": "CON-001",
                "tsc": "C1.1",
                "description": "Data classification and labeling policy",
                "type": "Preventive",
                "frequency": "Annual",
                "evidence": "Data classification policy, labeling standards, data inventory",
            },
            {
                "id": "CON-002",
                "tsc": "C1.1",
                "description": "Confidential data inventory and mapping",
                "type": "Detective",
                "frequency": "Quarterly",
                "evidence": "Data inventory, data flow diagrams, system classification",
            },
            {
                "id": "CON-003",
                "tsc": "C1.2",
                "description": "Encryption of confidential data at rest and in transit",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Encryption configuration, TLS settings, key management procedures",
            },
            {
                "id": "CON-004",
                "tsc": "C1.2",
                "description": "Access restrictions to confidential information",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Access control lists, need-to-know policy, access review records",
            },
            {
                "id": "CON-005",
                "tsc": "C1.2",
                "description": "Data loss prevention controls",
                "type": "Detective",
                "frequency": "Continuous",
                "evidence": "DLP configuration, DLP alerts/incidents, exception approvals",
            },
            {
                "id": "CON-006",
                "tsc": "C1.3",
                "description": "Secure data disposal and media sanitization",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Disposal procedures, sanitization certificates, destruction logs",
            },
            {
                "id": "CON-007",
                "tsc": "C1.3",
                "description": "Data retention enforcement and schedule compliance",
                "type": "Preventive",
                "frequency": "Quarterly",
                "evidence": "Retention schedule, deletion logs, retention compliance reports",
            },
        ],
    },
        "processing-integrity": {
        "name": "Processing Integrity",
        "controls": [
            {
                "id": "PRI-001",
                "tsc": "PI1.1",
                "description": "Input validation and data accuracy controls",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Validation rules, input sanitization config, error handling logs",
            },
            {
                "id": "PRI-002",
                "tsc": "PI1.1",
                "description": "Output verification and data integrity checks",
                "type": "Detective",
                "frequency": "Continuous",
                "evidence": "Reconciliation reports, checksum verification, output validation logs",
            },
            {
                "id": "PRI-003",
                "tsc": "PI1.2",
                "description": "Transaction completeness monitoring",
                "type": "Detective",
                "frequency": "Continuous",
                "evidence": "Transaction logs, reconciliation reports, completeness dashboards",
            },
            {
                "id": "PRI-004",
                "tsc": "PI1.2",
                "description": "Error handling and exception management",
                "type": "Corrective",
                "frequency": "Continuous",
                "evidence": "Error logs, exception handling procedures, retry mechanisms",
            },
            {
                "id": "PRI-005",
                "tsc": "PI1.3",
                "description": "Processing timeliness and SLA monitoring",
                "type": "Detective",
                "frequency": "Continuous",
                "evidence": "SLA reports, processing time metrics, batch job monitoring",
            },
            {
                "id": "PRI-006",
                "tsc": "PI1.4",
                "description": "Processing authorization and segregation of duties",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Authorization matrix, SoD controls, approval workflows",
            },
        ],
    },
    }
