# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_orchestrator_base import *  # noqa: F403,E402
# fmt: off
from agent_orchestrator_p1 import AgentConfig, AgentPattern  # noqa: E402,E501
# fmt: on


def generate_ascii_diagram(config: AgentConfig) -> str:
    """Generate ASCII workflow diagram"""
    lines = []

    # Header
    width = max(40, len(config.name) + 10)
    lines.append("┌" + "─" * width + "┐")
    lines.append("│" + config.name.center(width) + "│")
    lines.append("│" + f"({config.pattern.value} Pattern)".center(width) + "│")
    lines.append("└" + "─" * (width // 2 - 1) + "┬" + "─" * (width // 2) + "┘")
    lines.append(" " * (width // 2) + "│")

    # User Query
    lines.append(" " * (width // 2 - 8) + "┌───────────────┐")
    lines.append(" " * (width // 2 - 8) + "│  User Query   │")
    lines.append(" " * (width // 2 - 8) + "└───────┬───────┘")
    lines.append(" " * (width // 2) + "│")

    if config.pattern == AgentPattern.REACT:
        # ReAct loop
        lines.append(" " * (width // 2 - 8) + "┌───────────────┐")
        lines.append(" " * (width // 2 - 8) + "│    Think      │◄──────┐")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘       │")
        lines.append(" " * (width // 2) + "│               │")
        lines.append(" " * (width // 2 - 8) + "┌───────────────┐       │")
        lines.append(" " * (width // 2 - 8) + "│  Select Tool  │       │")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘       │")
        lines.append(" " * (width // 2) + "│               │")

        # Tools
        if config.tools:
            tool_line = "   ".join([f"[{t.name}]" for t in config.tools[:4]])
            if len(config.tools) > 4:
                tool_line += " ..."
            lines.append(" " * 4 + tool_line)
            lines.append(" " * (width // 2) + "│               │")

        lines.append(" " * (width // 2 - 8) + "┌───────────────┐       │")
        lines.append(" " * (width // 2 - 8) + "│   Observe     │───────┘")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘")

    elif config.pattern == AgentPattern.PLAN_EXECUTE:
        # Plan phase
        lines.append(" " * (width // 2 - 8) + "┌───────────────┐")
        lines.append(" " * (width // 2 - 8) + "│  Create Plan  │")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘")
        lines.append(" " * (width // 2) + "│")

        # Execute loop
        lines.append(" " * (width // 2 - 8) + "┌───────────────┐")
        lines.append(" " * (width // 2 - 8) + "│ Execute Step  │◄──────┐")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘       │")
        lines.append(" " * (width // 2) + "│               │")

        if config.tools:
            tool_line = "   ".join([f"[{t.name}]" for t in config.tools[:4]])
            lines.append(" " * 4 + tool_line)
            lines.append(" " * (width // 2) + "│               │")

        lines.append(" " * (width // 2 - 8) + "┌───────────────┐       │")
        lines.append(" " * (width // 2 - 8) + "│  Check Done?  │───────┘")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘")

    else:
        # Generic tool use
        lines.append(" " * (width // 2 - 8) + "┌───────────────┐")
        lines.append(" " * (width // 2 - 8) + "│ Process Query │")
        lines.append(" " * (width // 2 - 8) + "└───────┬───────┘")
        lines.append(" " * (width // 2) + "│")

        if config.tools:
            for tool in config.tools[:6]:
                lines.append(" " * (width // 2 - 8) + f"├──▶ [{tool.name}]")
            if len(config.tools) > 6:
                lines.append(" " * (width // 2 - 8) + "├──▶ [...]")

    # Final answer
    lines.append(" " * (width // 2) + "│")
    lines.append(" " * (width // 2 - 8) + "┌───────────────┐")
    lines.append(" " * (width // 2 - 8) + "│ Final Answer  │")
    lines.append(" " * (width // 2 - 8) + "└───────────────┘")

    return '\n'.join(lines)
def generate_mermaid_diagram(config: AgentConfig) -> str:
    """Generate Mermaid flowchart"""
    lines = ["```mermaid", "flowchart TD"]

    # Start and query
    lines.append(f"    subgraph {config.name}[{config.name}]")
    lines.append("    direction TB")
    lines.append("    A[User Query] --> B{Process}")

    if config.pattern == AgentPattern.REACT:
        lines.append("    B --> C[Think]")
        lines.append("    C --> D{Select Tool}")

        for i, tool in enumerate(config.tools[:6]):
            lines.append(f"    D -->|{tool.name}| T{i}[{tool.name}]")
            lines.append(f"    T{i} --> E[Observe]")

        lines.append("    E -->|Continue| C")
        lines.append("    E -->|Done| F[Final Answer]")

    elif config.pattern == AgentPattern.PLAN_EXECUTE:
        lines.append("    B --> P[Create Plan]")
        lines.append("    P --> X{Execute Step}")

        for i, tool in enumerate(config.tools[:6]):
            lines.append(f"    X -->|{tool.name}| T{i}[{tool.name}]")
            lines.append(f"    T{i} --> R[Review]")

        lines.append("    R -->|More Steps| X")
        lines.append("    R -->|Complete| F[Final Answer]")

    else:
        for i, tool in enumerate(config.tools[:6]):
            lines.append(f"    B -->|use| T{i}[{tool.name}]")
            lines.append(f"    T{i} --> F[Final Answer]")

    lines.append("    end")
    lines.append("```")

    return '\n'.join(lines)
