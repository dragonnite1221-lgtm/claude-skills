# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


def _format_text(report: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"Current Monthly Spend: ${report['current_monthly_usd']}")
    lines.append(f"Potential Savings:     ${report['potential_monthly_savings_usd']} ({report['savings_percentage']}%)")
    lines.append(f"Optimized Spend:       ${report['optimized_monthly_usd']}")
    lines.append("")

    lines.append("=== Priority Actions ===")
    for i, action in enumerate(report.get("priority_actions", []), 1):
        lines.append(f"  {i}. [{action['service']}] {action['recommendation']}")
        lines.append(f"     Savings: ${action.get('potential_savings_usd', 0)}")
    lines.append("")

    lines.append("=== All Recommendations ===")
    for rec in report.get("recommendations", []):
        lines.append(f"  [{rec['priority'].upper()}] {rec['service']} — {rec['type']}")
        lines.append(f"    Issue: {rec['issue']}")
        lines.append(f"    Action: {rec['recommendation']}")
        savings = rec.get("potential_savings_usd", 0)
        if savings:
            lines.append(f"    Savings: ${savings}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Azure Cost Optimizer — analyze Azure resources and recommend cost savings.",
        epilog="Examples:\n"
               "  python cost_optimizer.py --config resources.json\n"
               "  python cost_optimizer.py --config resources.json --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to JSON file with current Azure resource inventory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of human-readable text",
    )

    args = parser.parse_args()

    try:
        with open(args.config, "r") as f:
            resources = json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {args.config}: {exc}", file=sys.stderr)
        sys.exit(1)

    optimizer = AzureCostOptimizer(resources)
    report = optimizer.analyze()

    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        print(_format_text(report))
