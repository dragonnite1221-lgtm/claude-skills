# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentRole, CommunicationPattern  # noqa: F401,E501


class AgentPlannerMixin6:
    def _get_node_style(self, archetype: AgentRole) -> str:
        """Get node styling based on archetype"""
        styles = {
            AgentRole.COORDINATOR: ":::coordinator",
            AgentRole.SPECIALIST: ":::specialist", 
            AgentRole.INTERFACE: ":::interface",
            AgentRole.MONITOR: ":::monitor"
        }
        return styles.get(archetype, "")
    def _get_arrow_style(self, pattern: CommunicationPattern, criticality: str) -> str:
        """Get arrow styling based on communication pattern and criticality"""
        base_arrows = {
            CommunicationPattern.DIRECT_MESSAGE: "-->",
            CommunicationPattern.SHARED_STATE: "-.->",
            CommunicationPattern.EVENT_DRIVEN: "===>",
            CommunicationPattern.MESSAGE_QUEUE: "==="
        }
        
        arrow = base_arrows.get(pattern, "-->")
        
        # Modify for criticality
        if criticality == "high":
            return arrow
        elif criticality == "medium":
            return arrow.replace("-", ".")
        else:
            return arrow.replace("-", ":")
