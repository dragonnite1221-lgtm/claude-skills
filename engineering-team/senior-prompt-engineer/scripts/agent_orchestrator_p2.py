# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_orchestrator_base import *  # noqa: F403,E402
# fmt: off
from agent_orchestrator_p1 import AgentConfig, AgentPattern, ToolDefinition, ValidationResult, parse_yaml_simple  # noqa: E402,E501
# fmt: on


def load_config(path: Path) -> AgentConfig:
    """Load agent configuration from file"""
    content = path.read_text(encoding='utf-8')

    # Try JSON first
    if path.suffix == '.json':
        data = json.loads(content)
    else:
        # Try YAML
        try:
            data = parse_yaml_simple(content)
        except Exception:
            # Fallback to JSON if YAML parsing fails
            data = json.loads(content)

    # Parse pattern
    pattern_str = data.get('pattern', 'react').lower()
    try:
        pattern = AgentPattern(pattern_str)
    except ValueError:
        pattern = AgentPattern.CUSTOM

    # Parse tools
    tools = []
    for tool_data in data.get('tools', []):
        if isinstance(tool_data, dict):
            tools.append(ToolDefinition(
                name=tool_data.get('name', 'unknown'),
                description=tool_data.get('description', ''),
                parameters=tool_data.get('parameters', {}),
                required_config=tool_data.get('required_config', []),
                estimated_tokens=tool_data.get('estimated_tokens', 100)
            ))
        elif isinstance(tool_data, str):
            tools.append(ToolDefinition(name=tool_data, description=''))

    return AgentConfig(
        name=data.get('name', 'agent'),
        pattern=pattern,
        description=data.get('description', ''),
        tools=tools,
        max_iterations=int(data.get('max_iterations', 10)),
        system_prompt=data.get('system_prompt', ''),
        temperature=float(data.get('temperature', 0.7)),
        model=data.get('model', 'gpt-4')
    )
def validate_agent(config: AgentConfig) -> ValidationResult:
    """Validate agent configuration"""
    errors = []
    warnings = []
    tool_status = {}

    # Validate name
    if not config.name:
        errors.append("Agent name is required")

    # Validate tools
    if not config.tools:
        warnings.append("No tools defined - agent will have limited capabilities")

    tool_names = set()
    for tool in config.tools:
        # Check for duplicates
        if tool.name in tool_names:
            errors.append(f"Duplicate tool name: {tool.name}")
        tool_names.add(tool.name)

        # Check required config
        if tool.required_config:
            missing = [c for c in tool.required_config if not c.startswith('$')]
            if missing:
                tool_status[tool.name] = f"WARN: Missing config: {missing}"
            else:
                tool_status[tool.name] = "OK"
        else:
            tool_status[tool.name] = "OK - No config needed"

        # Check description
        if not tool.description:
            warnings.append(f"Tool '{tool.name}' has no description")

    # Validate pattern-specific requirements
    if config.pattern == AgentPattern.MULTI_AGENT:
        if len(config.tools) < 2:
            warnings.append("Multi-agent pattern typically requires 2+ specialized tools")

    # Check for potential infinite loops
    potential_loop = config.max_iterations > 50

    # Estimate tokens
    base_tokens = len(config.system_prompt.split()) * 1.3 if config.system_prompt else 200
    tool_tokens = sum(t.estimated_tokens for t in config.tools)

    min_tokens = int(base_tokens + tool_tokens)
    max_tokens = int((base_tokens + tool_tokens * 2) * config.max_iterations)

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        tool_status=tool_status,
        estimated_tokens_per_run=(min_tokens, max_tokens),
        potential_infinite_loop=potential_loop,
        max_depth=config.max_iterations
    )
