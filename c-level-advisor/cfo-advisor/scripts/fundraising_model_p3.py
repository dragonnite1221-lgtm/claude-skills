# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fundraising_model_base import *  # noqa: F403,E402
# fmt: off
from fundraising_model_p1 import CapTableEntry, ExitAnalysis, RoundResult  # noqa: E402,E501
# fmt: on


def fmt(value: float, prefix: str = "$") -> str:
    if value == float("inf"):
        return "∞"
    if abs(value) >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{prefix}{value/1_000:.0f}K"
    return f"{prefix}{value:.2f}"
def print_round_result(result: RoundResult, prev_cap_table: Optional[list[CapTableEntry]] = None) -> None:
    print(f"\n{'='*70}")
    print(f"  {result.round_name.upper()}")
    print(f"{'='*70}")
    print(f"  Pre-money valuation:   {fmt(result.pre_money_valuation)}")
    print(f"  Investment:            {fmt(result.investment_amount)}")
    print(f"  Post-money valuation:  {fmt(result.post_money_valuation)}")
    print(f"  Price per share:       {fmt(result.price_per_share, '$')}")
    print(f"  New shares issued:     {result.new_shares_issued:,.0f}")
    if result.option_pool_shares_created > 0:
        print(f"  Option pool created:   {result.option_pool_shares_created:,.0f} shares")
        print(f"  ⚠️  Pool created pre-round: dilutes existing shareholders, not new investor")
    print(f"  Total shares post:     {result.total_shares:,.0f}")

    print(f"\n  {'Shareholder':<22} {'Shares':>12} {'Ownership':>10}  {'Invested':>10}  {'Δ Ownership':>12}")
    print("  " + "-"*68)

    prev_map = {e.name: e.pct_ownership for e in prev_cap_table} if prev_cap_table else {}

    for entry in result.cap_table:
        delta = ""
        if entry.name in prev_map:
            change = (entry.pct_ownership - prev_map[entry.name]) * 100
            delta = f"{change:+.1f}pp"
        elif not entry.is_option_pool:
            delta = "new"

        invested_str = fmt(entry.invested) if entry.invested > 0 else "-"
        print(
            f"  {entry.name:<22} {entry.shares:>12,.0f} "
            f"{entry.pct_ownership*100:>9.2f}%  {invested_str:>10}  {delta:>12}"
        )
def print_exit_analysis(results: list[ExitAnalysis], exit_valuation: float) -> None:
    print(f"\n{'='*70}")
    print(f"  EXIT ANALYSIS @ {fmt(exit_valuation)} (all preferred converts to common)")
    print(f"{'='*70}")
    print(f"\n  {'Shareholder':<22} {'Ownership':>10} {'Proceeds':>12} {'Invested':>10} {'MOIC':>8}")
    print("  " + "-"*65)
    for r in results:
        moic_str = f"{r.moic:.1f}x" if r.moic > 0 else "n/a"
        invested_str = fmt(r.invested) if r.invested > 0 else "-"
        print(
            f"  {r.shareholder:<22} {r.ownership_pct*100:>9.2f}% "
            f"{fmt(r.proceeds_common):>12} {invested_str:>10} {moic_str:>8}"
        )
    print(f"\n  Note: Does not model liquidation preferences.")
    print(f"  Participating preferred reduces founder proceeds in most real exits.")
    print(f"  See references/fundraising_playbook.md for full liquidation waterfall.")
def print_dilution_summary(rounds: list[RoundResult]) -> None:
    print(f"\n{'='*70}")
    print(f"  DILUTION SUMMARY — FOUNDER PERSPECTIVE")
    print(f"{'='*70}")

    # Find all founders (common shareholders who aren't investors or option pool)
    founder_names = []
    for entry in rounds[0].cap_table:
        if entry.share_class == "common" and not entry.is_option_pool:
            founder_names.append(entry.name)

    if not founder_names:
        print("  No common shareholders found in initial cap table.")
        return

    header = f"  {'Round':<16}" + "".join(f"  {n:<16}" for n in founder_names) + f"  {'Total Inv':>12}"
    print(header)
    print("  " + "-" * (16 + 18 * len(founder_names) + 14))

    for result in rounds:
        cap_map = {e.name: e for e in result.cap_table}
        total_invested = sum(e.invested for e in result.cap_table if not e.is_option_pool)
        row = f"  {result.round_name:<16}"
        for name in founder_names:
            pct = cap_map[name].pct_ownership * 100 if name in cap_map else 0
            row += f"  {pct:>6.2f}%         "
        row += f"  {fmt(total_invested):>12}"
        print(row)
def export_csv_rounds(rounds: list[RoundResult]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Round", "Shareholder", "Share Class", "Shares", "Ownership Pct",
                     "Invested", "Pre Money", "Post Money", "Price Per Share"])
    for r in rounds:
        for entry in r.cap_table:
            writer.writerow([
                r.round_name, entry.name, entry.share_class,
                round(entry.shares, 0), round(entry.pct_ownership * 100, 4),
                round(entry.invested, 2), round(r.pre_money_valuation, 0),
                round(r.post_money_valuation, 0), round(r.price_per_share, 4),
            ])
    return buf.getvalue()
