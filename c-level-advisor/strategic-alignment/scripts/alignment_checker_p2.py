# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alignment_checker_base import *  # noqa: F403,E402
# fmt: off
from alignment_checker_p1 import _mod_cg0_0  # noqa: E402,E501
# fmt: on


def _mod_cg0_1():
    return {
        "teams": [
        {
            "name": "Sales",
            "okrs": [
                {
                    "id": "S1",
                    "objective": "Hit DACH new business targets",
                    "parent_company_okr_id": "C1",
                    "key_results": [
                        "Close 15 new DACH logos",
                        "Pipeline coverage: 3x of target",
                        "Average deal size > €18K ARR"
                    ],
                    "potential_conflicts": ["C3", "CS2"]
                },
                {
                    "id": "S2",
                    "objective": "Expand into Austria market",
                    "parent_company_okr_id": None,  # ORPHAN — no company OKR parent
                    "key_results": [
                        "5 qualified meetings with Austrian prospects",
                        "1 pilot signed in Austria"
                    ],
                    "potential_conflicts": []
                }
            ]
        },
        {
            "name": "Engineering",
            "okrs": [
                {
                    "id": "E1",
                    "objective": "Deliver API v1 on schedule",
                    "parent_company_okr_id": "C2",
                    "key_results": [
                        "API v1 feature complete by Week 8",
                        "Zero critical bugs at launch",
                        "P95 latency < 200ms under 500 RPS"
                    ],
                    "potential_conflicts": []
                },
                {
                    "id": "E2",
                    "objective": "Reduce infrastructure cost by 30%",
                    "parent_company_okr_id": "C3",
                    "key_results": [
                        "Migrate 3 services to spot instances",
                        "Decommission legacy DB cluster",
                        "Monthly infra cost < €12K"
                    ],
                    "potential_conflicts": []
                },
                {
                    "id": "E3",
                    "objective": "Achieve zero-downtime deployments",
                    "parent_company_okr_id": None,  # ORPHAN
                    "key_results": [
                        "Implement blue-green deployment pipeline",
                        "Deployment success rate > 99.5%"
                    ],
                    "potential_conflicts": []
                }
            ]
        },
        {
            "name": "Customer Success",
            "okrs": [
                {
                    "id": "CS1",
                    "objective": "Drive retention and expansion in DACH",
                    "parent_company_okr_id": "C1",
                    "key_results": [
                        "NRR > 110% for DACH cohort",
                        "Churn < 2% gross monthly",
                        "CSAT score > 4.5/5"
                    ],
                    "potential_conflicts": []
                },
                {
                    "id": "CS2",
                    "objective": "Reduce support ticket volume by 40%",
                    "parent_company_okr_id": "C3",
                    "key_results": [
                        "Launch self-serve knowledge base",
                        "Ticket deflection rate > 35%",
                        "Time-to-first-response < 2 hours"
                    ],
                    "potential_conflicts": ["S1"]  # Volume close pressure → more bad-fit customers → more tickets
                }
            ]
        },
        {
            "name": "Marketing",
            "okrs": [
                {
                    "id": "M1",
                    "objective": "Generate DACH pipeline to support sales targets",
                    "parent_company_okr_id": "C1",
                    "key_results": [
                        "€2.4M qualified pipeline from DACH",
                        "30 qualified demo requests from target ICP",
                        "CAC from inbound < €4K"
                    ],
                    "potential_conflicts": []
                }
            ]
        }
    ],
        "known_conflicts": [
        {
            "team_a": "Sales",
            "okr_a": "S1",
            "team_b": "Customer Success",
            "okr_b": "CS2",
            "description": "Sales closing volume deals to hit number may include poor-fit customers, increasing CS ticket load and reducing CSAT — directly conflicting with CS ticket reduction target."
        }
    ],
    }
SAMPLE_DATA = {**_mod_cg0_0(), **_mod_cg0_1()}
def get_all_company_okr_ids(data):
    return {okr["id"] for okr in data["company"]["okrs"]}
