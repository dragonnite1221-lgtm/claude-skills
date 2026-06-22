# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402


@dataclass
class ComponentInfo:
    """Information about a detected React component"""
    name: str
    file_path: str
    component_type: str  # 'functional', 'class', 'forwardRef', 'memo'
    has_props: bool
    props: List[str]
    has_hooks: List[str]
    has_context: bool
    has_effects: bool
    has_state: bool
    has_callbacks: bool
    exports: List[str]
    imports: List[str]


@dataclass
class TestCase:
    """A single test case to generate"""
    name: str
    description: str
    test_type: str  # 'render', 'interaction', 'a11y', 'props', 'state'
    code: str


@dataclass
class TestFile:
    """A complete test file to generate"""
    component: ComponentInfo
    test_cases: List[TestCase] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)
