# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402


def parse_teams(teams_str: str) -> List[str]:
    """Parse comma-separated team string into list"""
    if not teams_str:
        return None
    return [t.strip() for t in teams_str.split(',') if t.strip()]
