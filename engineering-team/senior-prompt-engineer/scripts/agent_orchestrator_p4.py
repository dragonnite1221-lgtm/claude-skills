# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_orchestrator_base import *  # noqa: F403,E402
# fmt: off
from agent_orchestrator_p1 import AgentConfig, ValidationResult  # noqa: E402,E501
from agent_orchestrator_p2 import validate_agent  # noqa: E402,E501
# fmt: on


def estimate_cost(config: AgentConfig, runs: int = 100) -> Dict[str, Any]:
    """Estimate token costs for agent runs"""
    validation = validate_agent(config)
    min_tokens, max_tokens = validation.estimated_tokens_per_run

    # Cost per 1K tokens
    costs = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'claude-3-opus': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
    }

    model_cost = costs.get(config.model, costs['gpt-4'])

    # Assume 60% input, 40% output
    input_tokens = min_tokens * 0.6
    output_tokens = min_tokens * 0.4

    cost_per_run_min = (input_tokens / 1000 * model_cost['input'] +
                        output_tokens / 1000 * model_cost['output'])

    input_tokens_max = max_tokens * 0.6
    output_tokens_max = max_tokens * 0.4
    cost_per_run_max = (input_tokens_max / 1000 * model_cost['input'] +
                        output_tokens_max / 1000 * model_cost['output'])

    return {
        'model': config.model,
        'tokens_per_run': {'min': min_tokens, 'max': max_tokens},
        'cost_per_run': {'min': round(cost_per_run_min, 4), 'max': round(cost_per_run_max, 4)},
        'estimated_monthly': {
            'runs': runs * 30,
            'cost_min': round(cost_per_run_min * runs * 30, 2),
            'cost_max': round(cost_per_run_max * runs * 30, 2)
        }
    }
def format_validation_report(config: AgentConfig, result: ValidationResult) -> str:
    """Format validation result as human-readable report"""
    lines = []
    lines.append("=" * 50)
    lines.append("AGENT VALIDATION REPORT")
    lines.append("=" * 50)
    lines.append("")

    lines.append(f"📋 AGENT INFO")
    lines.append(f"  Name:    {config.name}")
    lines.append(f"  Pattern: {config.pattern.value}")
    lines.append(f"  Model:   {config.model}")
    lines.append("")

    lines.append(f"🔧 TOOLS ({len(config.tools)} registered)")
    for tool in config.tools:
        status = result.tool_status.get(tool.name, "Unknown")
        emoji = "✅" if status.startswith("OK") else "⚠️"
        lines.append(f"  {emoji} {tool.name} - {status}")
    lines.append("")

    lines.append("📊 FLOW ANALYSIS")
    lines.append(f"  Max iterations:      {result.max_depth}")
    lines.append(f"  Estimated tokens:    {result.estimated_tokens_per_run[0]:,} - {result.estimated_tokens_per_run[1]:,}")
    lines.append(f"  Potential loop:      {'⚠️ Yes' if result.potential_infinite_loop else '✅ No'}")
    lines.append("")

    if result.errors:
        lines.append(f"❌ ERRORS ({len(result.errors)})")
        for error in result.errors:
            lines.append(f"  • {error}")
        lines.append("")

    if result.warnings:
        lines.append(f"⚠️ WARNINGS ({len(result.warnings)})")
        for warning in result.warnings:
            lines.append(f"  • {warning}")
        lines.append("")

    # Overall status
    if result.is_valid:
        lines.append("✅ VALIDATION PASSED")
    else:
        lines.append("❌ VALIDATION FAILED")

    lines.append("")
    lines.append("=" * 50)

    return '\n'.join(lines)
