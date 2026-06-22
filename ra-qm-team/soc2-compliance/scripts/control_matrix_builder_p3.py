# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from control_matrix_builder_base import *  # noqa: F403,E402
# fmt: off
from control_matrix_builder_p1 import _mod_cg1_0  # noqa: E402,E501
from control_matrix_builder_p2 import _mod_cg1_1  # noqa: E402,E501
# fmt: on


def _mod_cg1_2():
    return [
        {
                "id": "SEC-031",
                "tsc": "CC8.1",
                "description": "Change management authorization and testing",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Change tickets, approval records, test results, deployment logs",
            },
        {
                "id": "SEC-032",
                "tsc": "CC9.1",
                "description": "Vendor and business partner risk management",
                "type": "Preventive",
                "frequency": "Annual",
                "evidence": "Vendor risk assessments, vendor register, SOC 2 reports from vendors",
            },
        {
                "id": "SEC-033",
                "tsc": "CC9.2",
                "description": "Risk mitigation through insurance and other transfer mechanisms",
                "type": "Preventive",
                "frequency": "Annual",
                "evidence": "Insurance policies, risk transfer documentation",
            },
    ]
def _mod_cg0_0():
    return {
        "security": {
        "name": "Security (Common Criteria)",
        "controls": (_mod_cg1_0() + _mod_cg1_1() + _mod_cg1_2()),
    },
    }
def _mod_cg0_1():
    return {
        "availability": {
        "name": "Availability",
        "controls": [
            {
                "id": "AVL-001",
                "tsc": "A1.1",
                "description": "Capacity management and infrastructure scaling",
                "type": "Preventive",
                "frequency": "Continuous",
                "evidence": "Capacity monitoring dashboards, scaling policies, resource utilization reports",
            },
            {
                "id": "AVL-002",
                "tsc": "A1.1",
                "description": "System performance monitoring and SLA tracking",
                "type": "Detective",
                "frequency": "Continuous",
                "evidence": "Uptime reports, SLA dashboards, performance metrics",
            },
            {
                "id": "AVL-003",
                "tsc": "A1.2",
                "description": "Data backup procedures and verification",
                "type": "Preventive",
                "frequency": "Daily",
                "evidence": "Backup logs, backup success/failure reports, retention configuration",
            },
            {
                "id": "AVL-004",
                "tsc": "A1.2",
                "description": "Disaster recovery planning and documentation",
                "type": "Preventive",
                "frequency": "Annual",
                "evidence": "DR plan, BCP documentation, recovery procedures",
            },
            {
                "id": "AVL-005",
                "tsc": "A1.2",
                "description": "Business continuity management and communication",
                "type": "Preventive",
                "frequency": "Annual",
                "evidence": "BCP plan, communication tree, emergency contacts",
            },
            {
                "id": "AVL-006",
                "tsc": "A1.3",
                "description": "Disaster recovery testing and validation",
                "type": "Detective",
                "frequency": "Annual",
                "evidence": "DR test results, RTO/RPO measurements, test reports",
            },
            {
                "id": "AVL-007",
                "tsc": "A1.3",
                "description": "Failover testing and redundancy validation",
                "type": "Detective",
                "frequency": "Quarterly",
                "evidence": "Failover test records, redundancy configuration, test results",
            },
        ],
    },
    }
