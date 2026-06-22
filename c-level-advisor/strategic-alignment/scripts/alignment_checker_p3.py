# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alignment_checker_base import *  # noqa: F403,E402


def detect_orphans(data, company_ids):
    """Find team OKRs with no parent company OKR."""
    orphans = []
    for team in data["teams"]:
        for okr in team["okrs"]:
            if okr.get("parent_company_okr_id") is None:
                orphans.append({
                    "team": team["name"],
                    "okr_id": okr["id"],
                    "objective": okr["objective"]
                })
            elif okr["parent_company_okr_id"] not in company_ids:
                orphans.append({
                    "team": team["name"],
                    "okr_id": okr["id"],
                    "objective": okr["objective"],
                    "note": f"References non-existent company OKR: {okr['parent_company_okr_id']}"
                })
    return orphans
def detect_coverage_gaps(data, company_ids):
    """Find company OKRs with no team support."""
    coverage = defaultdict(list)
    for team in data["teams"]:
        for okr in team["okrs"]:
            parent = okr.get("parent_company_okr_id")
            if parent and parent in company_ids:
                coverage[parent].append({
                    "team": team["name"],
                    "okr_id": okr["id"],
                    "objective": okr["objective"]
                })

    gaps = []
    over_indexed = []
    for company_okr in data["company"]["okrs"]:
        cid = company_okr["id"]
        supporting = coverage.get(cid, [])
        entry = {
            "company_okr_id": cid,
            "objective": company_okr["objective"],
            "supporting_team_count": len(supporting),
            "supporting_teams": [s["team"] for s in supporting]
        }
        if len(supporting) == 0:
            gaps.append(entry)
        elif len(supporting) >= 4:
            over_indexed.append(entry)

    return gaps, over_indexed, coverage
def detect_conflicts(data):
    """Surface declared and potential OKR conflicts."""
    conflicts = []

    # Use declared known_conflicts
    for conflict in data.get("known_conflicts", []):
        conflicts.append({
            "type": "declared",
            "team_a": conflict["team_a"],
            "okr_a": conflict["okr_a"],
            "team_b": conflict["team_b"],
            "okr_b": conflict["okr_b"],
            "description": conflict["description"]
        })

    # Use potential_conflicts fields on OKRs for cross-reference
    okr_index = {}
    for team in data["teams"]:
        for okr in team["okrs"]:
            okr_index[okr["id"]] = {"team": team["name"], "objective": okr["objective"]}

    for team in data["teams"]:
        for okr in team["okrs"]:
            for conflict_id in okr.get("potential_conflicts", []):
                if conflict_id in okr_index:
                    target = okr_index[conflict_id]
                    # Avoid duplicate (A→B and B→A)
                    already_declared = any(
                        (c["okr_a"] == okr["id"] and c["okr_b"] == conflict_id) or
                        (c["okr_a"] == conflict_id and c["okr_b"] == okr["id"])
                        for c in conflicts
                    )
                    if not already_declared:
                        conflicts.append({
                            "type": "potential",
                            "team_a": team["name"],
                            "okr_a": okr["id"],
                            "team_b": target["team"],
                            "okr_b": conflict_id,
                            "description": f"Potential conflict between '{okr['objective']}' and '{target['objective']}' — review recommended"
                        })

    return conflicts
def compute_alignment_score(data, orphans, gaps, conflicts, coverage):
    """Score overall alignment from 0–100."""
    total_team_okrs = sum(len(t["okrs"]) for t in data["teams"])
    total_company_okrs = len(data["company"]["okrs"])

    orphan_penalty = (len(orphans) / max(total_team_okrs, 1)) * 30
    gap_penalty = (len(gaps) / max(total_company_okrs, 1)) * 30
    conflict_penalty = min(len(conflicts) * 10, 30)

    score = max(0, 100 - orphan_penalty - gap_penalty - conflict_penalty)
    return round(score)
def score_label(score):
    if score >= 85:
        return "✅ Excellent"
    elif score >= 70:
        return "🟡 Moderate misalignment"
    elif score >= 50:
        return "🟠 Significant misalignment"
    else:
        return "🔴 Critical misalignment"
