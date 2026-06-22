# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gws_recipe_runner_base import *  # noqa: F403,E402


@dataclass
class Recipe:
    name: str
    description: str
    category: str
    services: List[str]
    commands: List[str]
    prerequisites: str = ""
