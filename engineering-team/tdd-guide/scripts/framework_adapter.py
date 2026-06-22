# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from framework_adapter_base import *  # noqa: F403,E402
from framework_adapter_p0 import Framework, Language  # noqa: F401,E501
from framework_adapter_c0 import FrameworkAdapterMixin0  # noqa: F401
from framework_adapter_c1 import FrameworkAdapterMixin1  # noqa: F401
from framework_adapter_c2 import FrameworkAdapterMixin2  # noqa: F401
from framework_adapter_c3 import FrameworkAdapterMixin3  # noqa: F401


class FrameworkAdapter(FrameworkAdapterMixin0, FrameworkAdapterMixin1, FrameworkAdapterMixin2, FrameworkAdapterMixin3):
    pass
