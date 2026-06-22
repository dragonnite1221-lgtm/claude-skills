# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from portfolio_analyzer_base import *  # noqa: F403,E402
# fmt: off
from portfolio_analyzer_p1 import posture_color, quadrant_emoji, sample_data  # noqa: E402,E501
from portfolio_analyzer_p3 import analyze_portfolio, fmt_currency  # noqa: E402,E501
# fmt: on


def render_report(result: dict) -> str:
    lines = []
    lines.append("=" * 65)
    lines.append(f"  PORTFOLIO ANALYZER — {result['company']}")
    lines.append(f"  Total Quarterly Revenue: {fmt_currency(result['total_revenue_quarterly'])}")
    if result.get("total_engineering_headcount"):
        lines.append(f"  Engineering Headcount: {result['total_engineering_headcount']}")
    lines.append("=" * 65)
    lines.append("")

    # Portfolio health
    health = result["portfolio_health_score"]
    bar_len = 40
    filled = round(health * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    lines.append(f"  Portfolio Health: {health:.0%}")
    lines.append(f"  [{bar}]")
    lines.append("")

    # Quadrant summary
    lines.append("  QUADRANT SUMMARY")
    lines.append("  " + "-" * 55)
    header = f"  {'Quadrant':<15} {'Count':>5} {'Revenue':>10} {'Rev%':>6} {'Eng%':>6}"
    lines.append(header)
    lines.append("  " + "-" * 55)
    total_rev = result["total_revenue_quarterly"]
    for q in ["Star", "Cash Cow", "Question Mark", "Dog"]:
        qs = result["quadrant_summary"][q]
        emoji = quadrant_emoji(q)
        label = f"{emoji} {q}"
        rev_pct = f"{qs['revenue_pct']:.0%}" if qs["count"] else "-"
        eng = f"{qs['eng_pct']}%" if qs["count"] else "-"
        rev = fmt_currency(qs["revenue"]) if qs["count"] else "-"
        lines.append(f"  {label:<15} {qs['count']:>5} {rev:>10} {rev_pct:>6} {eng:>6}")
    lines.append("")

    # Per-product breakdown
    lines.append("  PRODUCT BREAKDOWN")
    lines.append("  " + "-" * 65)
    for p in result["products"]:
        emoji = quadrant_emoji(p["quadrant"])
        pc = posture_color(p["posture"])
        lines.append(
            f"  {emoji} {p['name']} — {p['quadrant']} → {pc} {p['posture']}"
        )
        lines.append(
            f"     Revenue: {fmt_currency(p['revenue_quarterly'])}/qtr  "
            f"QoQ: {p['qoq_growth']:+.0%}  "
            f"Mkt growth: {p['market_growth_pct']:+.0f}%"
        )
        lines.append(
            f"     Share ratio: {p['share_ratio']:.1f}x  "
            f"Eng: {p['eng_capacity_pct']}%  "
            f"Alignment: {p['alignment_score']:.0%}"
        )
        if p.get("d30_retention") is not None:
            lines.append(
                f"     D30 retention: {p['d30_retention']:.0%}  "
                f"NPS: {p['nps'] if p['nps'] is not None else 'N/A'}"
            )
        if p.get("notes"):
            lines.append(f"     Note: {p['notes']}")
        for f in p.get("findings", []):
            lines.append(f"     {f}")
        lines.append("")

    # Portfolio-level findings
    lines.append("  PORTFOLIO FINDINGS")
    lines.append("  " + "-" * 65)
    for f in result.get("portfolio_findings", []):
        lines.append(f"  {f}")
    lines.append("")
    lines.append("=" * 65)

    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(
        description="Portfolio Analyzer — BCG matrix classification and investment recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="JSON file with portfolio data (default: built-in sample data)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON result",
    )
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No input file provided — running with sample data.\n")
        data = sample_data()

    result = analyze_portfolio(data)

    if args.json:
        # Make result JSON-serializable
        def clean(obj):
            if isinstance(obj, dict):
                return {k: clean(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean(v) for v in obj]
            elif isinstance(obj, float):
                return round(obj, 4)
            return obj
        print(json.dumps(clean(result), indent=2))
    else:
        print(render_report(result))
