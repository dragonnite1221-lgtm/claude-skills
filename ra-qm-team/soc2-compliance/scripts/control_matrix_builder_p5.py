# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from control_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from control_matrix_builder_p3 import _mod_cg0_0, _mod_cg0_1  # noqa: E402,E501
from control_matrix_builder_p4 import _mod_cg0_2  # noqa: E402,E501
# fmt: on


def _mod_cg0_3():
    return {
        "privacy": {
        "name": "Privacy",
        "controls": [
            {
                "id": "PRV-001",
                "tsc": "P1.1",
                "description": "Privacy notice publication and data collection transparency",
                "type": "Preventive",
                "frequency": "Annual",
                "evidence": "Privacy policy, data collection notices, purpose statements",
            },
            {
                "id": "PRV-002",
                "tsc": "P2.1",
                "description": "Consent management and preference tracking",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Consent records, opt-in/opt-out mechanisms, preference center",
            },
            {
                "id": "PRV-003",
                "tsc": "P3.1",
                "description": "Data minimization and lawful collection",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Data collection audit, purpose limitation documentation, lawful basis records",
            },
            {
                "id": "PRV-004",
                "tsc": "P4.1",
                "description": "Purpose limitation and use restrictions",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Data use policy, purpose limitation controls, access restrictions",
            },
            {
                "id": "PRV-005",
                "tsc": "P4.2",
                "description": "Data retention schedules and disposal procedures",
                "type": "Preventive",
                "frequency": "Quarterly",
                "evidence": "Retention schedule, deletion logs, disposal certificates",
            },
            {
                "id": "PRV-006",
                "tsc": "P5.1",
                "description": "Data subject access request (DSAR) processing",
                "type": "Corrective",
                "frequency": "Continuous",
                "evidence": "DSAR log, response records, processing timelines",
            },
            {
                "id": "PRV-007",
                "tsc": "P5.2",
                "description": "Data correction and rectification rights",
                "type": "Corrective",
                "frequency": "Continuous",
                "evidence": "Correction request records, data update logs",
            },
            {
                "id": "PRV-008",
                "tsc": "P6.1",
                "description": "Third-party data sharing controls and notifications",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Data sharing agreements, third-party inventory, DPAs",
            },
            {
                "id": "PRV-009",
                "tsc": "P6.2",
                "description": "Breach notification procedures",
                "type": "Corrective",
                "frequency": "Continuous",
                "evidence": "Breach response plan, notification templates, incident records",
            },
            {
                "id": "PRV-010",
                "tsc": "P7.1",
                "description": "Data quality and accuracy verification",
                "type": "Detective",
                "frequency": "Quarterly",
                "evidence": "Data quality reports, accuracy checks, correction logs",
            },
            {
                "id": "PRV-011",
                "tsc": "P8.1",
                "description": "Privacy program monitoring and compliance reviews",
                "type": "Detective",
                "frequency": "Quarterly",
                "evidence": "Privacy audits, compliance dashboards, complaint tracking",
            },
        ],
    },
    }
TSC_CONTROLS: Dict[str, Dict[str, Any]] = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2(), **_mod_cg0_3()}
VALID_CATEGORIES = list(TSC_CONTROLS.keys())
def build_matrix(categories: List[str]) -> List[Dict[str, str]]:
    """Build a control matrix for the selected TSC categories."""
    matrix = []
    for cat in categories:
        if cat not in TSC_CONTROLS:
            continue
        cat_data = TSC_CONTROLS[cat]
        for ctrl in cat_data["controls"]:
            matrix.append(
                {
                    "control_id": ctrl["id"],
                    "tsc_criteria": ctrl["tsc"],
                    "category": cat_data["name"],
                    "description": ctrl["description"],
                    "control_type": ctrl["type"],
                    "frequency": ctrl["frequency"],
                    "evidence_required": ctrl["evidence"],
                    "owner": "TBD",
                    "status": "Not Started",
                }
            )
    return matrix
