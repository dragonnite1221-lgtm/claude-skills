# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402
from tdd_workflow_p0 import TDDPhase, WorkflowState  # noqa: F401,E501
from tdd_workflow_c0 import TDDWorkflowMixin0  # noqa: F401
from tdd_workflow_c1 import TDDWorkflowMixin1  # noqa: F401
from tdd_workflow_c2 import TDDWorkflowMixin2  # noqa: F401
from tdd_workflow_c3 import TDDWorkflowMixin3  # noqa: F401
from tdd_workflow_c4 import TDDWorkflowMixin4  # noqa: F401


class TDDWorkflow(TDDWorkflowMixin0, TDDWorkflowMixin1, TDDWorkflowMixin2, TDDWorkflowMixin3, TDDWorkflowMixin4):
    pass
