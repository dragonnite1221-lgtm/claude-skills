# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from stakeholder_mapper_base import *  # noqa: F403,E402
# fmt: off
from stakeholder_mapper_p1 import calculate_overall_alignment, classify_stakeholder, engagement_sequencing, find_critical_path, risk_flags  # noqa: E402,E501
from stakeholder_mapper_p2 import hr, render_grid  # noqa: E402,E501
# fmt: on


def print_report(data: Dict):
    initiative = data.get("initiative", "Unnamed Initiative")
    stakeholders = data["stakeholders"]
    
    # Validate and fill defaults
    for s in stakeholders:
        s.setdefault("interest", 5)
        s.setdefault("notes", "")
        s["influence"] = max(1, min(10, float(s["influence"])))
        s["alignment"] = max(1, min(10, float(s["alignment"])))
        s["interest"] = max(1, min(10, float(s["interest"])))
    
    print()
    print(hr("═"))
    print(f"  STAKEHOLDER ANALYSIS")
    print(f"  {initiative}")
    print(hr("═"))
    
    # Overall assessment
    overall = calculate_overall_alignment(stakeholders)
    print()
    print("OVERALL ASSESSMENT")
    print(hr())
    print(f"  Weighted alignment score: {overall['score']}/10")
    print(f"  Verdict: {overall['verdict']}")
    
    # Grid visualization
    print()
    print(hr())
    print(render_grid(stakeholders))
    
    # Stakeholder profiles by quadrant
    sequenced = engagement_sequencing(stakeholders)
    
    # Group by quadrant
    quadrants = {}
    for s in sequenced:
        q = s["quadrant"]
        if q not in quadrants:
            quadrants[q] = []
        quadrants[q].append(s)
    
    quadrant_order = ["Blocker", "Swing Vote", "Champion", "Supporter", "Bystander"]
    
    print()
    print("STAKEHOLDER PROFILES")
    print(hr())
    
    for q_name in quadrant_order:
        if q_name not in quadrants:
            continue
        group = quadrants[q_name]
        first = group[0]
        print()
        print(f"  {first['symbol']} {q_name.upper()}S  ({len(group)} stakeholder{'s' if len(group)>1 else ''})")
        print(f"  Strategy: {first['strategy']}")
        print()
        
        for s in group:
            cls = classify_stakeholder(s["influence"], s["alignment"])
            flags = risk_flags(s)
            
            print(f"    {s['name']}")
            print(f"    Role: {s.get('role', 'Not specified')}")
            print(f"    Influence: {'█'*int(s['influence']//2)}{'░'*(5-int(s['influence']//2))} {s['influence']:.0f}/10  "
                  f"Alignment: {'█'*int(s['alignment']//2)}{'░'*(5-int(s['alignment']//2))} {s['alignment']:.0f}/10  "
                  f"Interest: {'█'*int(s['interest']//2)}{'░'*(5-int(s['interest']//2))} {s['interest']:.0f}/10")
            
            if flags:
                for flag in flags:
                    print(f"    {flag}")
            
            if s.get("notes"):
                print(f"    Notes: {s['notes']}")
            
            print()
    
    # Engagement plan
    print()
    print("ENGAGEMENT PLAN (sequenced by priority)")
    print(hr())
    print()
    print(f"  {'#':<3} {'Name':<22} {'Quadrant':<14} {'Priority':<10} {'First Action'}")
    print(f"  {hr('-', 63)}")
    
    actions = {
        "Blocker": "Schedule 1:1 — understand specific objections",
        "Swing Vote": "Coffee or informal conversation — listen first",
        "Champion": "Brief them on the initiative — give them a role",
        "Supporter": "Keep informed — monthly update or email",
        "Bystander": "Include in standard comms only"
    }
    
    for i, s in enumerate(sequenced, 1):
        action = actions.get(s["quadrant"], "Maintain standard communication")
        print(f"  {i:<3} {s['name']:<22} {s['quadrant']:<14} {s['priority']:<10} {action}")
    
    # Risk summary
    print()
    print("RISK SUMMARY")
    print(hr())
    
    critical_path = find_critical_path(stakeholders)
    if critical_path:
        print()
        print("  High-influence stakeholders (outcome depends on these):")
        for s in critical_path:
            cls = classify_stakeholder(s["influence"], s["alignment"])
            alignment_label = "CHAMPION" if s["alignment"] >= 7 else "BLOCKER" if s["alignment"] <= 4 else "UNDECIDED"
            print(f"  {cls['symbol']} {s['name']:<25} influence {s['influence']:.0f}/10  → {alignment_label}")
    
    # All risk flags
    all_flags = []
    for s in stakeholders:
        flags = risk_flags(s)
        for flag in flags:
            all_flags.append((s["name"], flag))
    
    if all_flags:
        print()
        print("  Risk flags:")
        for name, flag in all_flags:
            print(f"  [{name}] {flag}")
    
    print()
    print(hr("═"))
    print()
