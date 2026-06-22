# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import Tool  # noqa: F401,E501


class AgentPlannerMixin4:
    def _identify_pipeline_stages(self, tasks: List[str]) -> List[str]:
        """Identify pipeline stages from task list"""
        # Common pipeline patterns
        common_stages = ["input", "process", "transform", "validate", "output"]
        
        # Try to infer stages from tasks
        stages = []
        task_text = " ".join(tasks).lower()
        
        if "collect" in task_text or "gather" in task_text:
            stages.append("collection")
        if "process" in task_text or "transform" in task_text:
            stages.append("processing")
        if "analyze" in task_text or "evaluate" in task_text:
            stages.append("analysis")
        if "validate" in task_text or "check" in task_text:
            stages.append("validation")
        if "output" in task_text or "deliver" in task_text or "report" in task_text:
            stages.append("output")
        
        # Default to common stages if none identified
        return stages if stages else common_stages[:min(5, len(tasks))]
    def _select_tools_for_domain(self, domain: str) -> List[Tool]:
        """Select appropriate tools for a specific domain"""
        domain_tools = {
            "research": [self.common_tools["web_search"], self.common_tools["data_analyzer"]],
            "development": [self.common_tools["code_executor"], self.common_tools["file_manager"]],
            "data": [self.common_tools["data_analyzer"], self.common_tools["file_manager"]],
            "communication": [self.common_tools["api_client"], self.common_tools["file_manager"]],
            "file": [self.common_tools["file_manager"]]
        }
        
        return domain_tools.get(domain, [self.common_tools["api_client"]])
    def _select_tools_for_stage(self, stage: str) -> List[Tool]:
        """Select appropriate tools for a pipeline stage"""
        stage_tools = {
            "input": [self.common_tools["api_client"], self.common_tools["file_manager"]],
            "collection": [self.common_tools["web_search"], self.common_tools["api_client"]],
            "process": [self.common_tools["code_executor"], self.common_tools["data_analyzer"]],
            "processing": [self.common_tools["data_analyzer"], self.common_tools["code_executor"]],
            "transform": [self.common_tools["data_analyzer"], self.common_tools["code_executor"]],
            "analysis": [self.common_tools["data_analyzer"]],
            "validate": [self.common_tools["data_analyzer"]],
            "validation": [self.common_tools["data_analyzer"]],
            "output": [self.common_tools["file_manager"], self.common_tools["api_client"]]
        }
        
        return stage_tools.get(stage, [self.common_tools["file_manager"]])
    def _select_diverse_tools(self) -> List[Tool]:
        """Select a diverse set of tools for general purpose agents"""
        return [
            self.common_tools["file_manager"],
            self.common_tools["code_executor"],
            self.common_tools["data_analyzer"]
        ]
