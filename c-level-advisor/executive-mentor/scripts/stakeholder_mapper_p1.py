# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from stakeholder_mapper_base import *  # noqa: F403,E402


def classify_stakeholder(influence: float, alignment: float) -> Dict:
    """
    Classify into strategic quadrant based on influence and alignment.
    
    Quadrants:
    - Champions (high influence, high alignment): Your most valuable assets
    - Blockers (high influence, low alignment): Your biggest risks
    - Supporters (low influence, high alignment): Useful but less critical
    - Bystanders (low influence, low alignment): Monitor, low priority
    - Swing Votes (medium influence, medium alignment): Key to persuade
    """
    mid_influence = 5.5
    mid_alignment = 5.5
    
    # Special case: swing votes — medium on both dimensions
    if 4 <= influence <= 7 and 4 <= alignment <= 7:
        return {
            "quadrant": "Swing Vote",
            "symbol": "⚡",
            "priority": "HIGH",
            "strategy": "Persuade — understand concerns, address directly, build relationship"
        }
    
    if influence >= mid_influence and alignment >= mid_alignment:
        return {
            "quadrant": "Champion",
            "symbol": "★",
            "priority": "HIGH",
            "strategy": "Leverage — activate them as advocates, give them a role in the initiative"
        }
    elif influence >= mid_influence and alignment < mid_alignment:
        return {
            "quadrant": "Blocker",
            "symbol": "✖",
            "priority": "CRITICAL",
            "strategy": "Address — understand their specific objections, find common ground or neutralize"
        }
    elif influence < mid_influence and alignment >= mid_alignment:
        return {
            "quadrant": "Supporter",
            "symbol": "○",
            "priority": "MEDIUM",
            "strategy": "Maintain — keep informed and engaged, potentially increase their influence"
        }
    else:
        return {
            "quadrant": "Bystander",
            "symbol": "·",
            "priority": "LOW",
            "strategy": "Monitor — minimal investment, keep informed with standard comms"
        }
def risk_flags(stakeholder: Dict) -> List[str]:
    """Identify specific risk signals for a stakeholder."""
    flags = []
    influence = stakeholder["influence"]
    alignment = stakeholder["alignment"]
    interest = stakeholder.get("interest", 5)
    
    if influence >= 7 and alignment <= 3:
        flags.append("🔴 HIGH-POWER BLOCKER — can kill this initiative")
    
    if influence >= 7 and alignment <= 5 and interest >= 7:
        flags.append("🟡 ENGAGED SKEPTIC — high influence, paying close attention, not convinced")
    
    if alignment <= 4 and interest >= 8:
        flags.append("🟡 ACTIVE OPPOSITION — low alignment but highly engaged — may mobilize others")
    
    if influence >= 6 and alignment >= 7 and interest <= 3:
        flags.append("🟡 DISENGAGED CHAMPION — strong supporter but not paying attention — needs activation")
    
    if influence >= 5 and 4 <= alignment <= 6:
        flags.append("⚡ PERSUADABLE — medium influence, genuinely undecided — high ROI to engage")
    
    return flags
def calculate_overall_alignment(stakeholders: List[Dict]) -> Dict:
    """Calculate weighted average alignment (weighted by influence)."""
    if not stakeholders:
        return {"score": 0, "verdict": "No data"}
    
    total_influence = sum(s["influence"] for s in stakeholders)
    if total_influence == 0:
        return {"score": 0, "verdict": "No influence"}
    
    weighted_alignment = sum(
        s["alignment"] * s["influence"] for s in stakeholders
    ) / total_influence
    
    if weighted_alignment >= 7:
        verdict = "FAVORABLE — strong support among influential stakeholders"
    elif weighted_alignment >= 5:
        verdict = "MIXED — significant opposition needs to be addressed"
    else:
        verdict = "UNFAVORABLE — initiative faces significant headwinds"
    
    return {
        "score": round(weighted_alignment, 2),
        "verdict": verdict
    }
def find_critical_path(stakeholders: List[Dict]) -> List[Dict]:
    """
    Identify the minimal set of stakeholders whose alignment is critical.
    These are high-influence stakeholders — their position determines the outcome.
    """
    high_influence = [s for s in stakeholders if s["influence"] >= 7]
    return sorted(high_influence, key=lambda x: x["influence"], reverse=True)
def engagement_sequencing(stakeholders: List[Dict]) -> List[Dict]:
    """
    Recommend engagement sequence.
    Order: Fix blockers → Activate champions → Persuade swing votes → Maintain rest.
    """
    classified = []
    for s in stakeholders:
        cls = classify_stakeholder(s["influence"], s["alignment"])
        classified.append({**s, **cls})
    
    # Sort by engagement priority
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    classified.sort(key=lambda x: (priority_order[x["priority"]], -x["influence"]))
    
    return classified
