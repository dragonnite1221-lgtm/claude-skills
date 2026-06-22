# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alignment_checker_base import *  # noqa: F403,E402
# fmt: off
from alignment_checker_p2 import SAMPLE_DATA, get_all_company_okr_ids  # noqa: E402,E501
from alignment_checker_p3 import compute_alignment_score, detect_conflicts, detect_coverage_gaps, detect_orphans, score_label  # noqa: E402,E501
# fmt: on


def print_report(data, orphans, gaps, over_indexed, conflicts, coverage, score):
    sep = "─" * 60

    print(f"\n{'═' * 60}")
    print(f"  STRATEGIC ALIGNMENT REPORT — {data.get('quarter', 'Unknown Quarter')}")
    print(f"  Company: {data['company']['name']}")
    print(f"{'═' * 60}\n")

    print(f"  ALIGNMENT SCORE: {score}/100  {score_label(score)}\n")
    print(sep)

    # Company OKRs summary
    print("\n📋 COMPANY OKRs\n")
    for okr in data["company"]["okrs"]:
        supporting = coverage.get(okr["id"], [])
        teams_str = ", ".join(s["team"] for s in supporting) if supporting else "⚠️  NONE"
        print(f"  [{okr['id']}] {okr['objective']}")
        print(f"       Supported by: {teams_str}")
    print()
    print(sep)

    # Orphan OKRs
    print(f"\n🔍 ORPHAN OKRs ({len(orphans)} found)\n")
    if orphans:
        for o in orphans:
            note = f" — {o.get('note', 'No parent company OKR assigned')}"
            print(f"  ⚠️  [{o['okr_id']}] {o['team']}: {o['objective']}")
            print(f"       Issue: {note}")
        print()
        print("  → Action: Connect each orphan to a company OKR, or deprioritize it.")
    else:
        print("  ✅ None found. All team OKRs connect to company OKRs.")
    print()
    print(sep)

    # Coverage gaps
    print(f"\n🕳️  COVERAGE GAPS ({len(gaps)} company OKRs with zero team support)\n")
    if gaps:
        for g in gaps:
            print(f"  🔴 [{g['company_okr_id']}] {g['objective']}")
            print(f"       No team is working on this. It will not be achieved.")
        print()
        print("  → Action: Assign at least one team owner to each unowned company OKR.")
    else:
        print("  ✅ All company OKRs have at least one team supporting them.")
    print()

    if over_indexed:
        print(f"  📊 OVER-INDEXED OKRs ({len(over_indexed)} company OKRs with 4+ teams)\n")
        for o in over_indexed:
            print(f"  [{o['company_okr_id']}] {o['objective']}")
            print(f"       {o['supporting_team_count']} teams: {', '.join(o['supporting_teams'])}")
        print()
        print("  → Note: High coverage isn't necessarily bad, but check if under-covered OKRs are being neglected.")
    print(sep)

    # Conflicts
    print(f"\n⚡ CONFLICTING OKRs ({len(conflicts)} found)\n")
    if conflicts:
        for i, c in enumerate(conflicts, 1):
            label = "🔴 Declared" if c["type"] == "declared" else "🟡 Potential"
            print(f"  {label} Conflict #{i}")
            print(f"    {c['team_a']} [{c['okr_a']}] ↔ {c['team_b']} [{c['okr_b']}]")
            print(f"    {c['description']}")
            print()
        print("  → Action: For each conflict, design a shared metric or shared constraint that prevents local optimization at company expense.")
    else:
        print("  ✅ No declared or potential conflicts detected.")
    print()
    print(sep)

    # Summary
    print("\n📊 SUMMARY\n")
    total_team_okrs = sum(len(t["okrs"]) for t in data["teams"])
    total_company_okrs = len(data["company"]["okrs"])
    print(f"  Company OKRs:       {total_company_okrs}")
    print(f"  Team OKRs:          {total_team_okrs}")
    print(f"  Orphan OKRs:        {len(orphans)}")
    print(f"  Coverage gaps:      {len(gaps)} of {total_company_okrs} company OKRs have no team support")
    print(f"  Conflicts:          {len(conflicts)}")
    print(f"  Alignment score:    {score}/100  {score_label(score)}")
    print()

    if score < 70:
        print("  ⚠️  RECOMMENDED ACTIONS:")
        if orphans:
            print(f"    1. Resolve {len(orphans)} orphan OKR(s) — connect to company goals or cut")
        if gaps:
            print(f"    2. Assign team owners to {len(gaps)} uncovered company OKR(s)")
        if conflicts:
            print(f"    3. Address {len(conflicts)} conflict(s) with shared metrics or constraints")
        print("    4. Run a cross-functional OKR review before next quarter begins")
    print()
    print(f"{'═' * 60}\n")
def main():
    parser = argparse.ArgumentParser(description="Strategic OKR Alignment Checker")
    parser.add_argument("--file", help="Path to JSON file with OKR data")
    parser.add_argument("--sample", action="store_true", help="Print sample JSON format and exit")
    args = parser.parse_args()

    if args.sample:
        print(json.dumps(SAMPLE_DATA, indent=2))
        return

    if args.file:
        try:
            with open(args.file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{args.file}': {e}")
            sys.exit(1)
    else:
        print("No file provided. Running with sample data.\n")
        print("To use your own data: python alignment_checker.py --file your_okrs.json")
        print("To see the expected JSON format: python alignment_checker.py --sample\n")
        data = SAMPLE_DATA

    # Run analysis
    company_ids = get_all_company_okr_ids(data)
    orphans = detect_orphans(data, company_ids)
    gaps, over_indexed, coverage = detect_coverage_gaps(data, company_ids)
    conflicts = detect_conflicts(data)
    score = compute_alignment_score(data, orphans, gaps, conflicts, coverage)

    # Print report
    print_report(data, orphans, gaps, over_indexed, conflicts, coverage, score)
