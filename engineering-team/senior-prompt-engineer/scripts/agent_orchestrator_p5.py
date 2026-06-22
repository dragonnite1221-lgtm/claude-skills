# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_orchestrator_base import *  # noqa: F403,E402
# fmt: off
from agent_orchestrator_p2 import load_config, validate_agent  # noqa: E402,E501
from agent_orchestrator_p3 import generate_ascii_diagram, generate_mermaid_diagram  # noqa: E402,E501
from agent_orchestrator_p4 import estimate_cost, format_validation_report  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Agent Orchestrator - Design and validate agent workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s agent.yaml --validate
  %(prog)s agent.yaml --visualize
  %(prog)s agent.yaml --visualize --format mermaid
  %(prog)s agent.yaml --estimate-cost --runs 100

Agent config format (YAML):

name: research_assistant
pattern: react
model: gpt-4
max_iterations: 10
tools:
  - name: web_search
    description: Search the web
    required_config: [api_key]
  - name: calculator
    description: Evaluate math expressions
        """
    )

    parser.add_argument('config', help='Agent configuration file (YAML or JSON)')
    parser.add_argument('--validate', '-V', action='store_true', help='Validate agent configuration')
    parser.add_argument('--visualize', '-v', action='store_true', help='Visualize agent workflow')
    parser.add_argument('--format', '-f', choices=['ascii', 'mermaid'], default='ascii',
                       help='Visualization format (default: ascii)')
    parser.add_argument('--estimate-cost', '-e', action='store_true', help='Estimate token costs')
    parser.add_argument('--runs', '-r', type=int, default=100, help='Daily runs for cost estimation')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Error parsing config: {e}", file=sys.stderr)
        sys.exit(1)

    # Default to validate if no action specified
    if not any([args.validate, args.visualize, args.estimate_cost]):
        args.validate = True

    output_parts = []

    # Validate
    if args.validate:
        result = validate_agent(config)
        if args.json:
            output_parts.append(json.dumps(asdict(result), indent=2))
        else:
            output_parts.append(format_validation_report(config, result))

    # Visualize
    if args.visualize:
        if args.format == 'mermaid':
            diagram = generate_mermaid_diagram(config)
        else:
            diagram = generate_ascii_diagram(config)
        output_parts.append(diagram)

    # Cost estimation
    if args.estimate_cost:
        costs = estimate_cost(config, args.runs)
        if args.json:
            output_parts.append(json.dumps(costs, indent=2))
        else:
            output_parts.append("")
            output_parts.append("💰 COST ESTIMATION")
            output_parts.append(f"  Model: {costs['model']}")
            output_parts.append(f"  Tokens per run: {costs['tokens_per_run']['min']:,} - {costs['tokens_per_run']['max']:,}")
            output_parts.append(f"  Cost per run: ${costs['cost_per_run']['min']:.4f} - ${costs['cost_per_run']['max']:.4f}")
            output_parts.append(f"  Monthly ({costs['estimated_monthly']['runs']:,} runs):")
            output_parts.append(f"    Min: ${costs['estimated_monthly']['cost_min']:.2f}")
            output_parts.append(f"    Max: ${costs['estimated_monthly']['cost_max']:.2f}")

    # Output
    output = '\n'.join(output_parts)
    print(output)

    if args.output:
        Path(args.output).write_text(output)
        print(f"\nOutput saved to {args.output}")
