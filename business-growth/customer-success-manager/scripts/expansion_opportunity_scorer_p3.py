# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from expansion_opportunity_scorer_base import *  # noqa: F403,E402
# fmt: off
from expansion_opportunity_scorer_p2 import analyse_expansion  # noqa: E402,E501
# fmt: on


def format_text(results: List[Dict[str, Any]]) -> str:
    """Format results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 72)
    lines.append("EXPANSION OPPORTUNITY REPORT")
    lines.append("=" * 72)
    lines.append("")

    total_rev = sum(r["total_estimated_revenue"] for r in results)
    total_opps = sum(r["opportunity_count"] for r in results)

    lines.append(f"Portfolio Summary: {len(results)} customers")
    lines.append(f"  Total Expansion Revenue Potential: ${total_rev:,.0f}")
    lines.append(f"  Total Opportunities Identified:    {total_opps}")
    lines.append("")

    # Sort customers by total estimated revenue descending
    sorted_results = sorted(results, key=lambda r: r["total_estimated_revenue"], reverse=True)

    for r in sorted_results:
        lines.append("-" * 72)
        lines.append(f"Customer: {r['name']} ({r['customer_id']})")
        lines.append(f"Segment:  {r['segment'].title()}  |  Current ARR: ${r['arr']:,.0f}")
        lines.append(f"Total Expansion Potential: ${r['total_estimated_revenue']:,.0f}  ({r['opportunity_count']} opportunities)")
        lines.append("")

        adoption = r["adoption_summary"]
        lines.append("  Adoption Summary:")
        lines.append(f"    Modules Adopted:    {adoption['adopted_modules']}/{adoption['total_modules']} ({adoption['adoption_rate']}%)")
        lines.append(f"    Avg Module Usage:   {adoption['avg_usage_pct']}%")
        lines.append(f"    Seat Utilisation:   {adoption['seat_utilisation']}%")
        lines.append(f"    Current Tier:       {adoption['current_tier'].title()}")
        lines.append(f"    Departments:        {adoption['departments_covered']} active, {adoption['departments_potential']} potential")

        if r["opportunities"]:
            lines.append("")
            lines.append("  Opportunities (ranked by priority):")
            for i, opp in enumerate(r["opportunities"], 1):
                opp_type = opp.get("type", "unknown").title()
                category = opp.get("category", "").replace("_", " ").title()
                rev = opp["estimated_revenue"]
                effort = opp.get("effort", "unknown").title()
                pri = opp.get("priority_score", 0)
                lines.append(f"    {i}. [{opp_type}] {category}")
                lines.append(f"       Revenue: ${rev:,.0f}  |  Effort: {effort}  |  Priority: {pri}")
                lines.append(f"       {opp.get('rationale', '')}")
        else:
            lines.append("")
            lines.append("  No expansion opportunities identified at this time.")

        lines.append("")

    lines.append("=" * 72)
    return "\n".join(lines)
def format_json(results: List[Dict[str, Any]]) -> str:
    """Format results as JSON."""
    total_rev = sum(r["total_estimated_revenue"] for r in results)
    total_opps = sum(r["opportunity_count"] for r in results)
    output = {
        "report": "expansion_opportunities",
        "summary": {
            "total_customers": len(results),
            "total_estimated_revenue": total_rev,
            "total_opportunities": total_opps,
        },
        "customers": sorted(results, key=lambda r: r["total_estimated_revenue"], reverse=True),
    }
    return json.dumps(output, indent=2)
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score expansion opportunities with adoption analysis and revenue estimation."
    )
    parser.add_argument("input_file", help="Path to JSON file containing customer data")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    customers = data.get("customers", [])
    if not customers:
        print("Error: No customer records found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [analyse_expansion(c) for c in customers]

    if args.output_format == "json":
        print(format_json(results))
    else:
        print(format_text(results))
