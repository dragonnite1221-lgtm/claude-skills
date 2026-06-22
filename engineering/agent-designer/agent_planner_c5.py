# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_planner_base import *  # noqa: F403,E402
from agent_planner_p0 import AgentArchitecturePattern, AgentDefinition, AgentRole, ArchitectureDesign, CommunicationLink, CommunicationPattern  # noqa: F401,E501


class AgentPlannerMixin5:
    def design_communication_topology(self, agents: List[AgentDefinition], pattern: AgentArchitecturePattern) -> List[CommunicationLink]:
        """Design communication links between agents"""
        links = []
        
        if pattern == AgentArchitecturePattern.SINGLE_AGENT:
            # No inter-agent communication needed
            return []
        
        elif pattern == AgentArchitecturePattern.SUPERVISOR:
            supervisor = next(agent for agent in agents if agent.archetype == AgentRole.COORDINATOR)
            specialists = [agent for agent in agents if agent.archetype == AgentRole.SPECIALIST]
            
            for specialist in specialists:
                # Bidirectional communication with supervisor
                links.append(CommunicationLink(
                    from_agent=supervisor.name,
                    to_agent=specialist.name,
                    pattern=CommunicationPattern.DIRECT_MESSAGE,
                    data_format="json",
                    frequency="on_demand",
                    criticality="high"
                ))
                links.append(CommunicationLink(
                    from_agent=specialist.name,
                    to_agent=supervisor.name,
                    pattern=CommunicationPattern.DIRECT_MESSAGE,
                    data_format="json",
                    frequency="on_completion",
                    criticality="high"
                ))
        
        elif pattern == AgentArchitecturePattern.SWARM:
            # All-to-all communication for swarm
            for i, agent1 in enumerate(agents):
                for j, agent2 in enumerate(agents):
                    if i != j:
                        links.append(CommunicationLink(
                            from_agent=agent1.name,
                            to_agent=agent2.name,
                            pattern=CommunicationPattern.EVENT_DRIVEN,
                            data_format="json",
                            frequency="periodic",
                            criticality="medium"
                        ))
        
        elif pattern == AgentArchitecturePattern.HIERARCHICAL:
            # Hierarchical communication based on dependencies
            for agent in agents:
                if agent.dependencies:
                    for dependency in agent.dependencies:
                        links.append(CommunicationLink(
                            from_agent=dependency,
                            to_agent=agent.name,
                            pattern=CommunicationPattern.DIRECT_MESSAGE,
                            data_format="json",
                            frequency="scheduled",
                            criticality="high"
                        ))
                        links.append(CommunicationLink(
                            from_agent=agent.name,
                            to_agent=dependency,
                            pattern=CommunicationPattern.DIRECT_MESSAGE,
                            data_format="json",
                            frequency="on_completion",
                            criticality="high"
                        ))
        
        elif pattern == AgentArchitecturePattern.PIPELINE:
            # Sequential pipeline communication
            for i in range(len(agents) - 1):
                links.append(CommunicationLink(
                    from_agent=agents[i].name,
                    to_agent=agents[i + 1].name,
                    pattern=CommunicationPattern.MESSAGE_QUEUE,
                    data_format="json",
                    frequency="continuous",
                    criticality="high"
                ))
        
        return links
    def generate_mermaid_diagram(self, design: ArchitectureDesign) -> str:
        """Generate Mermaid diagram for the architecture"""
        diagram = ["graph TD"]
        
        # Add agent nodes
        for agent in design.agents:
            node_style = self._get_node_style(agent.archetype)
            diagram.append(f"    {agent.name}[{agent.role}]{node_style}")
        
        # Add communication links
        for link in design.communication_topology:
            arrow_style = self._get_arrow_style(link.pattern, link.criticality)
            diagram.append(f"    {link.from_agent} {arrow_style} {link.to_agent}")
        
        # Add styling
        diagram.extend([
            "",
            "    classDef coordinator fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
            "    classDef specialist fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            "    classDef interface fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px",
            "    classDef monitor fill:#fff3e0,stroke:#e65100,stroke-width:2px"
        ])
        
        # Apply classes to nodes
        for agent in design.agents:
            class_name = agent.archetype.value
            diagram.append(f"    class {agent.name} {class_name}")
        
        return "\n".join(diagram)
