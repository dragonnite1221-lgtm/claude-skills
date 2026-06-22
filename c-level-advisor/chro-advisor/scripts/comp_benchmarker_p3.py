# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comp_benchmarker_base import *  # noqa: F403,E402
# fmt: off
from comp_benchmarker_p1 import CompRoster  # noqa: E402,E501
from comp_benchmarker_p2 import analyze_employee, bar, compa_ratio_distribution, fmt, pay_equity_audit  # noqa: E402,E501
# fmt: on


def print_report(roster: CompRoster):
    WIDTH = 76
    SEP = "=" * WIDTH
    sep = "-" * WIDTH

    analyses = [analyze_employee(e, roster) for e in roster.employees]
    cr_dist = compa_ratio_distribution(analyses)
    equity_audit = pay_equity_audit(analyses, roster.employees)

    print(SEP)
    print(f"  COMPENSATION BENCHMARKING REPORT — {roster.company}")
    print(f"  As of: {roster.as_of_date}  |  Stage: {roster.funding_stage}  |  Target: {roster.comp_philosophy_target}")
    print(SEP)

    # Summary stats
    total_emps = len(roster.employees)
    flagged = sum(1 for a in analyses if any(s in ["CRITICAL", "HIGH"] for s, _ in a["flags"]))
    total_payroll = sum(e.base_salary for e in roster.employees)
    avg_total_comp = sum(a["total_comp"] for a in analyses) // total_emps if total_emps else 0

    print(f"\n[ SUMMARY ]")
    print(sep)
    print(f"  Employees analyzed:      {total_emps}")
    print(f"  Flagged (critical/high): {flagged}")
    print(f"  Total base payroll:      {fmt(total_payroll)}/year")
    print(f"  Avg total comp:          {fmt(avg_total_comp)}/year")
    if cr_dist:
        print(f"  Avg compa-ratio:         {cr_dist['avg_compa_ratio']:.3f}")

    # Compa-ratio distribution
    if cr_dist:
        print(f"\n[ COMPA-RATIO DISTRIBUTION ]")
        print(sep)
        total_n = cr_dist["n"]
        for label, count in cr_dist["distribution"].items():
            pct = count / total_n if total_n else 0
            bar_str = bar(pct, 25)
            print(f"  {label:<30} {bar_str}  {count:3d} ({pct*100:4.0f}%)")

    # Pay equity audit
    print(f"\n[ PAY EQUITY AUDIT ]")
    print(sep)

    print(f"  By Gender:")
    for group, stats in equity_audit["gender"].items():
        gap = equity_audit["gender_gaps_pct"].get(group, 0.0)
        gap_str = f"  gap: {gap:+.1f}%" if gap != 0 else "  (reference group)"
        flag = " ⚠" if abs(gap) > 5 else ""
        print(f"    {group:<15} n={stats['n']}  avg_CR={stats['avg_cr']:.3f}{gap_str}{flag}")

    print(f"\n  By Ethnicity:")
    for group, stats in equity_audit["ethnicity"].items():
        gap = equity_audit["ethnicity_gaps_pct"].get(group, 0.0)
        gap_str = f"  gap: {gap:+.1f}%" if gap != 0 else "  (reference group)"
        flag = " ⚠" if abs(gap) > 5 else ""
        print(f"    {group:<20} n={stats['n']}  avg_CR={stats['avg_cr']:.3f}{gap_str}{flag}")

    print(f"\n  ⚠ = gap > 5%. Investigate with regression controlling for level, tenure, and performance.")

    # Employee detail with flags
    print(f"\n[ EMPLOYEE DETAIL ]")
    print(sep)

    # Group by function
    functions = sorted(set(e.function for e in roster.employees))
    for fn in functions:
        fn_analyses = [a for a in analyses if a["function"] == fn]
        if not fn_analyses:
            continue
        print(f"\n  ── {fn} ──")
        print(f"  {'Name':<22} {'Role':<28} {'Lvl':<5} {'Base':>10} {'TotalComp':>11} {'CR':>6} {'Perf':>5}  Flags")
        print(f"  {'-'*22} {'-'*28} {'-'*5} {'-'*10} {'-'*11} {'-'*6} {'-'*5}  {'-'*20}")

        for a in sorted(fn_analyses, key=lambda x: -x["base"]):
            cr_str = f"{a['compa_ratio']:.2f}" if a["compa_ratio"] else "N/A"
            flag_summary = ", ".join(s for s, _ in a["flags"] if s in ("CRITICAL", "HIGH", "MEDIUM"))
            flag_str = flag_summary if flag_summary else "OK"
            print(f"  {a['name']:<22} {a['role']:<28} {a['level']:<5} "
                  f"{fmt(a['base']):>10} {fmt(a['total_comp']):>11} {cr_str:>6} {a['performance']:>5}  {flag_str}")

            # Print flag detail for critical/high
            for severity, msg in a["flags"]:
                if severity in ("CRITICAL", "HIGH"):
                    print(f"  {'':>22}   ↳ [{severity}] {msg}")

    # Action items
    critical = [(a["name"], msg) for a in analyses for sev, msg in a["flags"] if sev == "CRITICAL"]
    high = [(a["name"], msg) for a in analyses for sev, msg in a["flags"] if sev == "HIGH"]
    medium = [(a["name"], msg) for a in analyses for sev, msg in a["flags"] if sev == "MEDIUM"]

    print(f"\n[ ACTION ITEMS ]")
    print(sep)

    if critical:
        print(f"\n  CRITICAL — Address this review cycle:")
        for name, msg in critical:
            print(f"    • {name}: {msg}")

    if high:
        print(f"\n  HIGH — Address within 30 days:")
        for name, msg in high[:10]:
            print(f"    • {name}: {msg}")
        if len(high) > 10:
            print(f"    ... and {len(high)-10} more")

    if medium:
        print(f"\n  MEDIUM — Address in next comp cycle:")
        for name, msg in medium[:8]:
            print(f"    • {name}: {msg}")
        if len(medium) > 8:
            print(f"    ... and {len(medium)-8} more")

    if not critical and not high and not medium:
        print(f"\n  No critical or high-severity issues. Compensation appears well-managed.")

    # Remediation cost estimate
    below_min = [a for a in analyses if a["band"] and a["base"] < a["band"].band_min]
    below_mid = [a for a in analyses if a["compa_ratio"] and a["compa_ratio"] < 0.90]

    if below_min or below_mid:
        print(f"\n[ REMEDIATION COST ESTIMATE ]")
        print(sep)

        if below_min:
            cost_to_min = sum(a["band"].band_min - a["base"] for a in below_min)
            print(f"  Cost to bring below-minimum to band min:  {fmt(cost_to_min)}/year  ({len(below_min)} employees)")

        if below_mid:
            cost_to_90 = sum(int(a["band"].band_mid * 0.90) - a["base"] for a in below_mid if a["base"] < int(a["band"].band_mid * 0.90))
            cost_to_90 = max(0, cost_to_90)
            print(f"  Cost to bring CR < 0.90 to CR = 0.90:    {fmt(cost_to_90)}/year  ({len(below_mid)} employees)")

        total_payroll_impact = sum(e.base_salary for e in roster.employees)
        total_remediation = (below_min and cost_to_min or 0)
        print(f"\n  Total payroll before remediation:  {fmt(total_payroll_impact)}/year")
        print(f"  Remediation as % of payroll:       {total_remediation/total_payroll_impact*100:.1f}%")

    print(f"\n{SEP}\n")
