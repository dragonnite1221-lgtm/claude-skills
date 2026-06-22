# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402


@dataclass
class RouteInfo:
    """Information about a detected route"""
    path: str  # URL path e.g., /dashboard
    file_path: str  # File system path
    route_type: str  # 'page', 'layout', 'api', 'dynamic'
    has_params: bool
    params: List[str]
    has_form: bool
    has_auth: bool
    interactions: List[str]
@dataclass
class TestSpec:
    """A Playwright test specification"""
    route: RouteInfo
    test_cases: List[str]
    imports: Set[str] = field(default_factory=set)
@dataclass
class PageObject:
    """Page Object Model class definition"""
    name: str
    route: str
    locators: List[Tuple[str, str, str]]  # (name, selector, description)
    methods: List[Tuple[str, str]]  # (name, code)
