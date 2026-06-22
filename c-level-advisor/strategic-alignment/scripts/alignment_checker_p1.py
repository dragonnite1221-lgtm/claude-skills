# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alignment_checker_base import *  # noqa: F403,E402


def _mod_cg0_0():
    return {
        "quarter": "Q2 2026",
        "company": {
        "name": "Acme Corp",
        "okrs": [
            {
                "id": "C1",
                "objective": "Win mid-market DACH healthcare segment",
                "key_results": [
                    "Reach 50 paying customers in DACH by EoQ",
                    "Achieve €800K ARR in DACH",
                    "Net Revenue Retention > 110%"
                ]
            },
            {
                "id": "C2",
                "objective": "Ship the platform API to unlock partner integrations",
                "key_results": [
                    "API v1 launched with 3 partner integrations",
                    "API documentation coverage: 100% of endpoints",
                    "< 200ms P95 response time under load"
                ]
            },
            {
                "id": "C3",
                "objective": "Build a capital-efficient growth engine",
                "key_results": [
                    "CAC payback period < 12 months",
                    "Burn multiple < 1.5x",
                    "Revenue per employee up 20% vs Q1"
                ]
            }
        ]
    },
    }
