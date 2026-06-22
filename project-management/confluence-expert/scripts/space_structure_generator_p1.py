# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from space_structure_generator_base import *  # noqa: F403,E402


BASE_SECTIONS = [
    {
        "title": "Home",
        "description": "Space landing page with quick links and team overview",
        "labels": ["home", "landing"],
        "children": [],
    },
    {
        "title": "Getting Started",
        "description": "Onboarding guide for new team members",
        "labels": ["onboarding", "getting-started"],
        "children": [
            {"title": "Team Charter", "labels": ["charter"]},
            {"title": "Tools & Access", "labels": ["tools", "access"]},
            {"title": "Communication Guidelines", "labels": ["communication"]},
            {"title": "Key Contacts", "labels": ["contacts"]},
        ],
    },
    {
        "title": "Meeting Notes",
        "description": "Recurring and ad-hoc meeting documentation",
        "labels": ["meetings"],
        "children": [
            {"title": "Weekly Standups", "labels": ["standup", "recurring"]},
            {"title": "Team Syncs", "labels": ["sync", "recurring"]},
            {"title": "Ad-hoc Meetings", "labels": ["ad-hoc"]},
        ],
    },
    {
        "title": "Templates",
        "description": "Reusable page templates for the team",
        "labels": ["templates"],
        "children": [],
    },
    {
        "title": "Archive",
        "description": "Archived and deprecated content",
        "labels": ["archive"],
        "children": [],
    },
]
