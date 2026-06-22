# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentArchitecturePattern, Tool  # noqa: F401,E501


class AgentPlannerMixin0:
    """Multi-agent system architecture planner"""
    def __init__(self):
        self.common_tools = self._define_common_tools()
        self.pattern_heuristics = self._define_pattern_heuristics()
    def _define_common_tools(self) -> Dict[str, Tool]:
        """Define commonly used tools across agents"""
        return {
            "web_search": Tool(
                name="web_search",
                description="Search the web for information",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"results": {"type": "array"}}},
                capabilities=["research", "information_gathering"],
                reliability="high",
                latency="medium"
            ),
            "code_executor": Tool(
                name="code_executor",
                description="Execute code in various languages",
                input_schema={"type": "object", "properties": {"language": {"type": "string"}, "code": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"result": {"type": "string"}, "error": {"type": "string"}}},
                capabilities=["code_execution", "testing", "automation"],
                reliability="high",
                latency="low"
            ),
            "file_manager": Tool(
                name="file_manager",
                description="Manage files and directories",
                input_schema={"type": "object", "properties": {"action": {"type": "string"}, "path": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"success": {"type": "boolean"}, "content": {"type": "string"}}},
                capabilities=["file_operations", "data_management"],
                reliability="high",
                latency="low"
            ),
            "data_analyzer": Tool(
                name="data_analyzer",
                description="Analyze and process data",
                input_schema={"type": "object", "properties": {"data": {"type": "object"}, "analysis_type": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"insights": {"type": "array"}, "metrics": {"type": "object"}}},
                capabilities=["data_analysis", "statistics", "visualization"],
                reliability="high",
                latency="medium"
            ),
            "api_client": Tool(
                name="api_client",
                description="Make API calls to external services",
                input_schema={"type": "object", "properties": {"url": {"type": "string"}, "method": {"type": "string"}, "data": {"type": "object"}}},
                output_schema={"type": "object", "properties": {"response": {"type": "object"}, "status": {"type": "integer"}}},
                capabilities=["integration", "external_services"],
                reliability="medium",
                latency="medium"
            )
        }
    def _define_pattern_heuristics(self) -> Dict[AgentArchitecturePattern, Dict[str, Any]]:
        """Define heuristics for selecting architecture patterns"""
        return {
            AgentArchitecturePattern.SINGLE_AGENT: {
                "team_size_range": (1, 1),
                "task_complexity": "simple",
                "coordination_overhead": "none",
                "suitable_for": ["simple tasks", "prototyping", "single domain"],
                "scaling_limit": "low"
            },
            AgentArchitecturePattern.SUPERVISOR: {
                "team_size_range": (2, 8),
                "task_complexity": "medium",
                "coordination_overhead": "low",
                "suitable_for": ["hierarchical tasks", "clear delegation", "quality control"],
                "scaling_limit": "medium"
            },
            AgentArchitecturePattern.SWARM: {
                "team_size_range": (3, 20),
                "task_complexity": "high",
                "coordination_overhead": "high",
                "suitable_for": ["parallel processing", "distributed problem solving", "fault tolerance"],
                "scaling_limit": "high"
            },
            AgentArchitecturePattern.HIERARCHICAL: {
                "team_size_range": (5, 50),
                "task_complexity": "very high",
                "coordination_overhead": "medium",
                "suitable_for": ["large organizations", "complex workflows", "enterprise systems"],
                "scaling_limit": "very high"
            },
            AgentArchitecturePattern.PIPELINE: {
                "team_size_range": (3, 15),
                "task_complexity": "medium",
                "coordination_overhead": "low",
                "suitable_for": ["sequential processing", "data pipelines", "assembly line tasks"],
                "scaling_limit": "medium"
            }
        }
