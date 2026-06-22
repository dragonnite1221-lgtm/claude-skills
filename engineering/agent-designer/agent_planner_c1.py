# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentArchitecturePattern, AgentDefinition, AgentRole, SystemRequirements  # noqa: F401,E501


class AgentPlannerMixin1:
    def select_architecture_pattern(self, requirements: SystemRequirements) -> AgentArchitecturePattern:
        """Select the most appropriate architecture pattern based on requirements"""
        team_size = requirements.team_size
        task_count = len(requirements.tasks)
        performance_reqs = requirements.performance_requirements
        
        # Score each pattern based on requirements
        pattern_scores = {}
        
        for pattern, heuristics in self.pattern_heuristics.items():
            score = 0
            
            # Team size fit
            min_size, max_size = heuristics["team_size_range"]
            if min_size <= team_size <= max_size:
                score += 3
            elif abs(team_size - min_size) <= 2 or abs(team_size - max_size) <= 2:
                score += 1
            
            # Task complexity assessment
            complexity_indicators = [
                "parallel" in requirements.description.lower(),
                "sequential" in requirements.description.lower(),
                "hierarchical" in requirements.description.lower(),
                "distributed" in requirements.description.lower(),
                task_count > 5,
                len(requirements.constraints) > 3
            ]
            
            complexity_score = sum(complexity_indicators)
            
            if pattern == AgentArchitecturePattern.SINGLE_AGENT and complexity_score <= 2:
                score += 2
            elif pattern == AgentArchitecturePattern.SUPERVISOR and 2 <= complexity_score <= 4:
                score += 2
            elif pattern == AgentArchitecturePattern.PIPELINE and "sequential" in requirements.description.lower():
                score += 3
            elif pattern == AgentArchitecturePattern.SWARM and "parallel" in requirements.description.lower():
                score += 3
            elif pattern == AgentArchitecturePattern.HIERARCHICAL and complexity_score >= 4:
                score += 2
            
            # Performance requirements
            if performance_reqs.get("high_throughput", False) and pattern in [AgentArchitecturePattern.SWARM, AgentArchitecturePattern.PIPELINE]:
                score += 2
            if performance_reqs.get("fault_tolerance", False) and pattern == AgentArchitecturePattern.SWARM:
                score += 2
            if performance_reqs.get("low_latency", False) and pattern in [AgentArchitecturePattern.SINGLE_AGENT, AgentArchitecturePattern.PIPELINE]:
                score += 1
            
            pattern_scores[pattern] = score
        
        # Select the highest scoring pattern
        best_pattern = max(pattern_scores.items(), key=lambda x: x[1])[0]
        return best_pattern
    def design_agents(self, requirements: SystemRequirements, pattern: AgentArchitecturePattern) -> List[AgentDefinition]:
        """Design individual agents based on requirements and architecture pattern"""
        agents = []
        
        if pattern == AgentArchitecturePattern.SINGLE_AGENT:
            agents = self._design_single_agent(requirements)
        elif pattern == AgentArchitecturePattern.SUPERVISOR:
            agents = self._design_supervisor_agents(requirements)
        elif pattern == AgentArchitecturePattern.SWARM:
            agents = self._design_swarm_agents(requirements)
        elif pattern == AgentArchitecturePattern.HIERARCHICAL:
            agents = self._design_hierarchical_agents(requirements)
        elif pattern == AgentArchitecturePattern.PIPELINE:
            agents = self._design_pipeline_agents(requirements)
        
        return agents
    def _design_single_agent(self, requirements: SystemRequirements) -> List[AgentDefinition]:
        """Design a single general-purpose agent"""
        all_tools = list(self.common_tools.values())
        
        agent = AgentDefinition(
            name="universal_agent",
            role="Universal Task Handler",
            archetype=AgentRole.SPECIALIST,
            responsibilities=requirements.tasks,
            capabilities=["general_purpose", "multi_domain", "adaptable"],
            tools=all_tools,
            communication_interfaces=["direct_user_interface"],
            constraints={
                "max_concurrent_tasks": 1,
                "memory_limit": "high",
                "response_time": "fast"
            },
            success_criteria=["complete all assigned tasks", "maintain quality standards", "respond within time limits"],
            dependencies=[]
        )
        
        return [agent]
