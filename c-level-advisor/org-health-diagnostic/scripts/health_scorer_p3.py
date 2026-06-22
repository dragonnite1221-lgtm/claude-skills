# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from health_scorer_base import *  # noqa: F403,E402
# fmt: off
from health_scorer_p1 import Dimension, Metric, STAGE_WEIGHTS, Stage, TrafficLight, Trend  # noqa: E402,E501
# fmt: on


def build_market_dimension(**kwargs) -> Dimension:
    return Dimension(
        key="market",
        name="Market Health",
        owner="CMO",
        emoji="📣",
        metrics=[
            Metric("Organic pipeline % ", kwargs.get("organic_pipeline_pct"), "%", 40, 20),
            Metric("Competitive win rate (%)", kwargs.get("competitive_win_rate"), "%", 45, 30),
            Metric("CAC trend (1=worsening, 5=improving)", kwargs.get("cac_trend_score"), "scale", 4, 2),
        ],
        trend=kwargs.get("market_trend", Trend.UNKNOWN),
    )
def calculate_overall(dimensions: List[Dimension], stage: Stage) -> Optional[float]:
    weights = STAGE_WEIGHTS[stage]
    total_weight = 0.0
    weighted_sum = 0.0
    for dim in dimensions:
        score = dim.score()
        w = weights.get(dim.key, 0.0)
        if score is not None and w > 0:
            weighted_sum += score * w
            total_weight += w
    if total_weight == 0:
        return None
    return round(weighted_sum / total_weight, 1)
def trend_arrow(trend: Trend) -> str:
    return {
        Trend.IMPROVING: "↑",
        Trend.STABLE: "→",
        Trend.DECLINING: "↓",
        Trend.UNKNOWN: "?",
    }[trend]
def traffic_light_icon(tl: TrafficLight) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}[tl.value]
def print_dashboard(dimensions: List[Dimension], overall: Optional[float],
                    stage: Stage, company: str = "Company") -> None:
    """Print the full health dashboard."""
    print("\n" + "=" * 65)
    print(f"ORG HEALTH DIAGNOSTIC — {company.upper()}")
    print(f"Stage: {stage.value.replace('_', ' ').title()}")
    if overall is not None:
        overall_tl = TrafficLight.GREEN if overall >= 7 else (TrafficLight.YELLOW if overall >= 4 else TrafficLight.RED)
        print(f"Overall: {traffic_light_icon(overall_tl)} {overall}/10")
    print("=" * 65)

    print("\nDIMENSION SCORES")
    print("─" * 65)

    priority_reds = []
    priority_yellows = []

    for dim in dimensions:
        score = dim.score()
        tl = dim.traffic_light()
        icon = traffic_light_icon(tl)
        trend = trend_arrow(dim.trend)
        coverage = int(dim.coverage() * 100)

        score_str = f"{score:.1f}" if score is not None else "N/A"
        cov_str = f"({coverage}% data)" if coverage < 100 else ""
        print(f"{dim.emoji} {dim.name:<22} {icon} {score_str:<5} {trend}  {dim.owner}  {cov_str}")

        if tl == TrafficLight.RED and score is not None:
            priority_reds.append(dim)
        elif tl == TrafficLight.YELLOW and score is not None:
            priority_yellows.append(dim)

    # Top priorities
    if priority_reds or priority_yellows:
        print(f"\n{'─' * 65}")
        print("PRIORITIES")
        print("─" * 65)

        idx = 1
        for dim in priority_reds[:3]:
            print(f"\n🔴 [{idx}] {dim.name} — Score: {dim.score():.1f}/10")
            # Show worst metric
            worst = min(
                [m for m in dim.metrics if m.score() is not None],
                key=lambda m: m.score(),
                default=None
            )
            if worst:
                print(f"   Worst metric: {worst.name} = {worst.value}{worst.unit}")
            missing = dim.missing_metrics()
            if missing:
                print(f"   Missing data: {', '.join(missing)}")
            idx += 1

        for dim in priority_yellows[:2]:
            print(f"\n🟡 [{idx}] {dim.name} — Score: {dim.score():.1f}/10 — {trend_arrow(dim.trend)}")
            idx += 1

    # Data gaps
    all_missing = [(dim.name, dim.missing_metrics()) for dim in dimensions if dim.missing_metrics()]
    if all_missing:
        print(f"\n{'─' * 65}")
        print("DATA GAPS (fill to improve diagnostic accuracy)")
        for dim_name, metrics in all_missing:
            print(f"  {dim_name}: {', '.join(metrics)}")

    # Cascade warnings
    print(f"\n{'─' * 65}")
    print("CASCADE RISK")
    red_keys = {d.key for d in dimensions if d.traffic_light() == TrafficLight.RED}
    if "people" in red_keys:
        print("  ⚠️  People RED → Engineering velocity drop expected in 60-90 days")
    if "engineering" in red_keys:
        print("  ⚠️  Engineering RED → Product quality at risk; roadmap will slip")
    if "product" in red_keys:
        print("  ⚠️  Product RED → Revenue retention at risk within 2 quarters")
    if "revenue" in red_keys:
        print("  ⚠️  Revenue RED → Financial pressure mounting; watch runway")
    if "financial" in red_keys:
        print("  🚨 Financial RED → All dimensions at risk; immediate board action needed")
    if not red_keys:
        print("  ✅ No active cascade risks detected")

    print(f"\n{'=' * 65}\n")
