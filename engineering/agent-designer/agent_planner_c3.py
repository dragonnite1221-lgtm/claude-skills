# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentDefinition, AgentRole, SystemRequirements  # noqa: F401,E501


class AgentPlannerMixin3:
    def _design_hierarchical_agents(self, requirements: SystemRequirements) -> List[AgentDefinition]:
        """Design hierarchical pattern agents"""
        agents = []
        
        # Create management hierarchy
        levels = min(3, requirements.team_size // 3)  # Reasonable hierarchy depth
        agents_per_level = requirements.team_size // levels
        
        # Top level manager
        manager = AgentDefinition(
            name="executive_manager",
            role="Executive Manager",
            archetype=AgentRole.COORDINATOR,
            responsibilities=["strategic_planning", "resource_allocation", "performance_monitoring"],
            capabilities=["leadership", "strategy", "resource_management", "oversight"],
            tools=[self.common_tools["data_analyzer"], self.common_tools["file_manager"]],
            communication_interfaces=["executive_dashboard", "management_messaging"],
            constraints={"management_span": 5, "decision_authority": "high"},
            success_criteria=["achieve system goals", "optimize resource usage", "maintain quality"],
            dependencies=[]
        )
        agents.append(manager)
        
        # Middle managers
        for i in range(agents_per_level - 1):
            middle_manager = AgentDefinition(
                name=f"team_manager_{i+1}",
                role=f"Team Manager #{i+1}",
                archetype=AgentRole.COORDINATOR,
                responsibilities=["team_coordination", "task_distribution", "progress_tracking"],
                capabilities=["team_management", "coordination", "reporting"],
                tools=[self.common_tools["file_manager"]],
                communication_interfaces=["management_messaging", "team_messaging"],
                constraints={"team_size": 3, "reporting_frequency": "hourly"},
                success_criteria=["team performance", "task completion", "team satisfaction"],
                dependencies=["executive_manager"]
            )
            agents.append(middle_manager)
        
        # Workers
        remaining_agents = requirements.team_size - len(agents)
        for i in range(remaining_agents):
            worker = AgentDefinition(
                name=f"worker_agent_{i+1}",
                role=f"Task Worker #{i+1}",
                archetype=AgentRole.SPECIALIST,
                responsibilities=["task_execution", "result_delivery", "status_reporting"],
                capabilities=["task_execution", "specialized_skills", "reliability"],
                tools=self._select_diverse_tools(),
                communication_interfaces=["team_messaging"],
                constraints={"task_focus": "single", "reporting_interval": "30min"},
                success_criteria=["complete assigned tasks", "maintain quality", "meet deadlines"],
                dependencies=[f"team_manager_{(i // 3) + 1}"]
            )
            agents.append(worker)
        
        return agents
    def _design_pipeline_agents(self, requirements: SystemRequirements) -> List[AgentDefinition]:
        """Design pipeline pattern agents"""
        agents = []
        
        # Create sequential processing stages
        pipeline_stages = self._identify_pipeline_stages(requirements.tasks)
        
        for i, stage in enumerate(pipeline_stages):
            agent = AgentDefinition(
                name=f"pipeline_stage_{i+1}_{stage}",
                role=f"Pipeline Stage {i+1}: {stage.title()}",
                archetype=AgentRole.SPECIALIST,
                responsibilities=[f"process_{stage}", f"validate_{stage}_output", "handoff_to_next_stage"],
                capabilities=[f"{stage}_processing", "quality_control", "data_transformation"],
                tools=self._select_tools_for_stage(stage),
                communication_interfaces=["pipeline_queue", "stage_messaging"],
                constraints={
                    "processing_order": i + 1,
                    "batch_size": 10,
                    "stage_timeout": "5min"
                },
                success_criteria=[f"successfully process {stage}", "maintain data integrity", "meet throughput targets"],
                dependencies=[f"pipeline_stage_{i}_{pipeline_stages[i-1]}"] if i > 0 else []
            )
            agents.append(agent)
        
        return agents
    def _identify_task_domains(self, tasks: List[str]) -> List[str]:
        """Identify distinct domains from task list"""
        domains = []
        domain_keywords = {
            "research": ["research", "search", "find", "investigate", "analyze"],
            "development": ["code", "build", "develop", "implement", "program"],
            "data": ["data", "process", "analyze", "calculate", "compute"],
            "communication": ["write", "send", "message", "communicate", "report"],
            "file": ["file", "document", "save", "load", "manage"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in " ".join(tasks).lower() for keyword in keywords):
                domains.append(domain)
        
        return domains[:5]  # Limit to 5 domains
