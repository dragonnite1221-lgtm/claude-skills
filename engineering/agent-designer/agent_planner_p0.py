# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402


class AgentArchitecturePattern(Enum):
    """Supported agent architecture patterns"""
    SINGLE_AGENT = "single_agent"
    SUPERVISOR = "supervisor"
    SWARM = "swarm"
    HIERARCHICAL = "hierarchical"
    PIPELINE = "pipeline"


class CommunicationPattern(Enum):
    """Agent communication patterns"""
    DIRECT_MESSAGE = "direct_message"
    SHARED_STATE = "shared_state"
    EVENT_DRIVEN = "event_driven"
    MESSAGE_QUEUE = "message_queue"


class AgentRole(Enum):
    """Standard agent role archetypes"""
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    INTERFACE = "interface"
    MONITOR = "monitor"


@dataclass
class Tool:
    """Tool definition for agents"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    capabilities: List[str]
    reliability: str = "high"  # high, medium, low
    latency: str = "low"       # low, medium, high


@dataclass
class AgentDefinition:
    """Complete agent definition"""
    name: str
    role: str
    archetype: AgentRole
    responsibilities: List[str]
    capabilities: List[str]
    tools: List[Tool]
    communication_interfaces: List[str]
    constraints: Dict[str, Any]
    success_criteria: List[str]
    dependencies: List[str] = None


@dataclass
class CommunicationLink:
    """Communication link between agents"""
    from_agent: str
    to_agent: str
    pattern: CommunicationPattern
    data_format: str
    frequency: str
    criticality: str


@dataclass
class SystemRequirements:
    """Input system requirements"""
    goal: str
    description: str
    tasks: List[str]
    constraints: Dict[str, Any]
    team_size: int
    performance_requirements: Dict[str, Any]
    safety_requirements: List[str]
    integration_requirements: List[str]
    scale_requirements: Dict[str, Any]


@dataclass
class ArchitectureDesign:
    """Complete architecture design output"""
    pattern: AgentArchitecturePattern
    agents: List[AgentDefinition]
    communication_topology: List[CommunicationLink]
    shared_resources: List[Dict[str, Any]]
    guardrails: List[Dict[str, Any]]
    scaling_strategy: Dict[str, Any]
    failure_handling: Dict[str, Any]
