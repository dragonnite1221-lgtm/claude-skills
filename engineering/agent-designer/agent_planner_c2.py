# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentDefinition, AgentRole, SystemRequirements  # noqa: F401,E501


class AgentPlannerMixin2:
    def _design_supervisor_agents(self, requirements: SystemRequirements) -> List[AgentDefinition]:
        """Design supervisor pattern agents"""
        agents = []
        
        # Create supervisor agent
        supervisor = AgentDefinition(
            name="supervisor_agent",
            role="Task Coordinator and Quality Controller",
            archetype=AgentRole.COORDINATOR,
            responsibilities=[
                "task_decomposition",
                "delegation",
                "progress_monitoring",
                "quality_assurance",
                "result_aggregation"
            ],
            capabilities=["planning", "coordination", "evaluation", "decision_making"],
            tools=[self.common_tools["file_manager"], self.common_tools["data_analyzer"]],
            communication_interfaces=["user_interface", "agent_messaging"],
            constraints={
                "max_concurrent_supervisions": 5,
                "decision_timeout": "30s"
            },
            success_criteria=["successful task completion", "optimal resource utilization", "quality standards met"],
            dependencies=[]
        )
        agents.append(supervisor)
        
        # Create specialist agents based on task domains
        task_domains = self._identify_task_domains(requirements.tasks)
        for i, domain in enumerate(task_domains[:requirements.team_size - 1]):
            specialist = AgentDefinition(
                name=f"{domain}_specialist",
                role=f"{domain.title()} Specialist",
                archetype=AgentRole.SPECIALIST,
                responsibilities=[task for task in requirements.tasks if domain in task.lower()],
                capabilities=[f"{domain}_expertise", "specialized_tools", "domain_knowledge"],
                tools=self._select_tools_for_domain(domain),
                communication_interfaces=["supervisor_messaging"],
                constraints={
                    "domain_scope": domain,
                    "task_queue_size": 10
                },
                success_criteria=[f"excel in {domain} tasks", "maintain domain expertise", "provide quality output"],
                dependencies=["supervisor_agent"]
            )
            agents.append(specialist)
        
        return agents
    def _design_swarm_agents(self, requirements: SystemRequirements) -> List[AgentDefinition]:
        """Design swarm pattern agents"""
        agents = []
        
        # Create peer agents with overlapping capabilities
        agent_count = min(requirements.team_size, 10)  # Reasonable swarm size
        base_capabilities = ["collaboration", "consensus", "adaptation", "peer_communication"]
        
        for i in range(agent_count):
            agent = AgentDefinition(
                name=f"swarm_agent_{i+1}",
                role=f"Collaborative Worker #{i+1}",
                archetype=AgentRole.SPECIALIST,
                responsibilities=requirements.tasks,  # All agents can handle all tasks
                capabilities=base_capabilities + [f"specialization_{i%3}"],  # Some specialization
                tools=list(self.common_tools.values()),
                communication_interfaces=["peer_messaging", "broadcast", "consensus_protocol"],
                constraints={
                    "peer_discovery_timeout": "10s",
                    "consensus_threshold": 0.6,
                    "max_retries": 3
                },
                success_criteria=["contribute to group goals", "maintain peer relationships", "adapt to failures"],
                dependencies=[f"swarm_agent_{j+1}" for j in range(agent_count) if j != i]
            )
            agents.append(agent)
        
        return agents
