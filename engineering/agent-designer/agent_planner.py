# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentArchitecturePattern, AgentDefinition, AgentRole, ArchitectureDesign, CommunicationLink, CommunicationPattern, SystemRequirements, Tool  # noqa: F401,E501
from agent_planner_p1 import main  # noqa: F401,E501
from agent_planner_c0 import AgentPlannerMixin0  # noqa: F401
from agent_planner_c1 import AgentPlannerMixin1  # noqa: F401
from agent_planner_c2 import AgentPlannerMixin2  # noqa: F401
from agent_planner_c3 import AgentPlannerMixin3  # noqa: F401
from agent_planner_c4 import AgentPlannerMixin4  # noqa: F401
from agent_planner_c5 import AgentPlannerMixin5  # noqa: F401
from agent_planner_c6 import AgentPlannerMixin6  # noqa: F401
from agent_planner_c7 import AgentPlannerMixin7  # noqa: F401
from agent_planner_c8 import AgentPlannerMixin8  # noqa: F401


class AgentPlanner(AgentPlannerMixin0, AgentPlannerMixin1, AgentPlannerMixin2, AgentPlannerMixin3, AgentPlannerMixin4, AgentPlannerMixin5, AgentPlannerMixin6, AgentPlannerMixin7, AgentPlannerMixin8):
    pass


if __name__ == "__main__":
    main()