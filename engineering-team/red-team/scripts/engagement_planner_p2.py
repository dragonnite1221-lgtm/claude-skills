# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from engagement_planner_base import *  # noqa: F403,E402
# fmt: off
from engagement_planner_p1 import ACCESS_LEVEL_HIERARCHY, KILL_CHAIN_PHASE_ORDER, MITRE_TECHNIQUES, OPSEC_RISKS  # noqa: E402,E501
# fmt: on


def build_engagement_plan(techniques_input, access_level, crown_jewels, target_count):
    """
    Core planning algorithm. Returns (plan_dict, scope_violations_count).
    """
    provided_level = ACCESS_LEVEL_HIERARCHY[access_level]
    valid_techniques = []
    scope_violations = []
    not_found = []

    for tid in techniques_input:
        tid = tid.strip().upper()
        if tid not in MITRE_TECHNIQUES:
            not_found.append(tid)
            continue
        tech = MITRE_TECHNIQUES[tid]
        required_level = ACCESS_LEVEL_HIERARCHY[tech["access_level"]]
        if required_level > provided_level:
            scope_violations.append({
                "technique_id": tid,
                "technique_name": tech["name"],
                "reason": (
                    f"Requires '{tech['access_level']}' access; "
                    f"provided access level is '{access_level}'"
                ),
            })
            continue
        effort_score = round(tech["detection_risk"] * (len(tech["prerequisites"]) + 1), 4)
        valid_techniques.append({
            "id": tid,
            "name": tech["name"],
            "tactic": tech["tactic"],
            "detection_risk": tech["detection_risk"],
            "prerequisites": tech["prerequisites"],
            "effort_score": effort_score,
        })

    # Group by tactic and order phases by kill chain
    tactic_map = {}
    for t in valid_techniques:
        tactic_map.setdefault(t["tactic"], []).append(t)

    phases = []
    tactics_present = set(tactic_map.keys())
    for phase_name in KILL_CHAIN_PHASE_ORDER:
        if phase_name in tactic_map:
            techniques_in_phase = sorted(
                tactic_map[phase_name], key=lambda x: x["effort_score"], reverse=True
            )
            phases.append({
                "phase": phase_name,
                "techniques": techniques_in_phase,
            })

    # Identify choke points
    # A choke point is a credential_access or privilege_escalation technique
    # that other selected techniques list as a prerequisite dependency,
    # especially relevant when crown jewels are specified.
    choke_tactic_set = {"credential_access", "privilege_escalation"}
    choke_points = []
    for t in valid_techniques:
        if t["tactic"] not in choke_tactic_set:
            continue
        # Count how many other techniques depend on this tactic
        dependents = [
            other["id"]
            for other in valid_techniques
            if t["tactic"] in other["prerequisites"] and other["id"] != t["id"]
        ]
        # If crown jewels are specified, flag anything in those choke tactics
        crown_jewel_relevant = bool(crown_jewels)
        if dependents or crown_jewel_relevant:
            choke_points.append({
                "technique_id": t["id"],
                "technique_name": t["name"],
                "tactic": t["tactic"],
                "dependent_technique_count": len(dependents),
                "dependent_techniques": dependents,
                "crown_jewel_relevant": crown_jewel_relevant,
                "note": (
                    "Blocking this technique disrupts the downstream kill-chain. "
                    "Priority hardening target."
                ),
            })

    # Collect OPSEC risks for tactics present in the selected techniques
    seen_risks = set()
    applicable_opsec = []
    for risk_item in OPSEC_RISKS:
        relevant = risk_item["relevant_tactics"]
        # Include universal risks (empty relevant_tactics list) always
        if not relevant or tactics_present.intersection(relevant):
            key = risk_item["risk"]
            if key not in seen_risks:
                seen_risks.add(key)
                applicable_opsec.append(risk_item)

    # Estimate duration: sum detection_risk * 2 days per phase, minimum 3 days
    raw_duration = sum(
        tech["detection_risk"] * 2
        for t in valid_techniques
        for tech in [t]  # flatten
    )
    # Per-phase minimum: ensure at least 0.5 day per phase
    phase_count = len(phases)
    estimated_days = max(3.0, round(raw_duration + phase_count * 0.5, 1))

    # Scale by target_count (each additional target adds 20% duration)
    if target_count and target_count > 1:
        estimated_days = round(estimated_days * (1 + (target_count - 1) * 0.2), 1)

    # Required authorizations list
    required_authorizations = [
        "Signed Rules of Engagement (RoE) document",
        "Written executive/CISO authorization",
        "Defined scope and out-of-scope assets list",
        "Emergency stop contact and escalation path",
        "Deconfliction process with SOC/Blue Team",
    ]
    if "impact" in tactics_present:
        required_authorizations.append(
            "Specific written authorization for destructive/impact techniques (T14xx)"
        )
    if "credential_access" in tactics_present:
        required_authorizations.append(
            "Written authorization for credential capture and handling procedures"
        )

    plan = {
        "engagement_summary": {
            "access_level": access_level,
            "crown_jewels": crown_jewels,
            "target_count": target_count or 1,
            "techniques_requested": len(techniques_input),
            "techniques_valid": len(valid_techniques),
            "techniques_not_found": not_found,
            "estimated_duration_days": estimated_days,
        },
        "phases": phases,
        "choke_points": choke_points,
        "opsec_risks": applicable_opsec,
        "scope_violations": scope_violations,
        "required_authorizations": required_authorizations,
    }
    return plan, len(scope_violations)
