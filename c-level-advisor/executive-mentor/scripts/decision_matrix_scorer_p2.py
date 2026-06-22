# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_matrix_scorer_base import *  # noqa: F403,E402
# fmt: off
from decision_matrix_scorer_p1 import close_call_analysis, criterion_breakdown, hr, normalize_weights, score_all, score_option, sensitivity_analysis  # noqa: E402,E501
# fmt: on


def print_report(data: Dict):
    """Print the full decision analysis report."""
    decision = data.get("decision", "Unnamed Decision")
    criteria = normalize_weights(data["criteria"])
    options = data["options"]
    
    print()
    print(hr("═"))
    print(f"  DECISION MATRIX ANALYSIS")
    print(f"  {decision}")
    print(hr("═"))
    
    # ── Criteria summary
    print()
    print("CRITERIA & WEIGHTS")
    print(hr())
    for c in sorted(criteria, key=lambda x: x["weight"], reverse=True):
        bar_len = int(c["weight"] * 30)
        bar = "█" * bar_len
        desc = f"  — {c['description']}" if c.get("description") else ""
        print(f"  {c['name']:<25} {c['weight']*100:>5.1f}%  {bar}{desc}")
    
    # ── Scoring results
    print()
    print("RESULTS (ranked)")
    print(hr())
    results = score_all(options, criteria)
    max_score = 10.0  # max possible weighted score
    for rank, (name, score) in enumerate(results, 1):
        pct = score / 10.0
        bar_len = int(pct * 40)
        bar = "█" * bar_len
        medal = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"#{rank} "
        print(f"  {medal} {name:<25} {score:>5.2f}/10  {bar}")
    
    winner = results[0][0]
    print()
    print(f"  ► Winner: {winner}  (score: {results[0][1]:.2f})")
    
    # ── Close calls
    close = close_call_analysis(results)
    if close:
        print()
        print("CLOSE CALLS")
        print(hr())
        for c in close:
            print(f"  ⚠  {c['name']}: {c['score']:.2f}  (gap: {c['gap_pct']}% — {c['verdict']})")
    
    # ── Per-criterion breakdown
    print()
    print("SCORE BREAKDOWN BY CRITERION")
    print(hr())
    breakdown = criterion_breakdown(options, criteria)
    
    # Header
    opt_names = [opt["name"][:16] for opt in options]
    header = f"  {'Criterion':<22}"
    for n in opt_names:
        header += f"  {n:>10}"
    print(header)
    print("  " + hr("-", 63))
    
    for c in criteria:
        row = f"  {c['name']:<22}"
        for opt in options:
            raw = opt["scores"].get(c["name"], 5)
            row += f"  {raw:>10}"
        row += f"  (weight {c['weight']*100:.0f}%)"
        print(row)
    
    # Weighted row
    print("  " + hr("-", 63))
    weighted_row = f"  {'Weighted Total':<22}"
    for name, score in results:
        # Re-order by options list order
        weighted_row += f"  {score:>10.2f}"
    # Actually print in options order
    print(f"  {'Weighted Total':<22}", end="")
    for opt in options:
        s = score_option(opt, criteria)
        print(f"  {s:>10.2f}", end="")
    print()
    
    # ── Sensitivity analysis
    print()
    print("SENSITIVITY ANALYSIS")
    print(hr())
    print("  How much does the winner change if we adjust criterion weights?")
    print()
    sensitivity = sensitivity_analysis(options, criteria)
    for crit_name, result in sensitivity.items():
        if result["stable"]:
            print(f"  ✓ {crit_name:<28} STABLE — winner holds at ±30% weight change")
        else:
            print(f"  ⚠ {crit_name:<28} FRAGILE — flips to '{result['flip_to']}' at {result['flip_at']}")
    
    # ── Recommendation
    print()
    print("RECOMMENDATION")
    print(hr())
    unstable = [k for k, v in sensitivity.items() if not v["stable"]]
    if unstable:
        print(f"  Winner: {winner}")
        print(f"  Confidence: MEDIUM — result is sensitive to weights on: {', '.join(unstable)}")
        print()
        print("  Before committing:")
        print(f"  • Validate that your weighting of [{', '.join(unstable)}] is correct")
        print("  • Consider whether the weight differences reflect genuine priorities")
        print("  • If uncertain, run scenario with alternative weights")
    else:
        print(f"  Winner: {winner}")
        print(f"  Confidence: HIGH — winner is stable across all weight scenarios")
        print()
        print("  The decision is clear. The main risk is whether your scoring")
        print("  of each option on each criterion is accurate.")
    
    print()
    print(hr("═"))
    print()
