# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from activation_funnel_analyzer_base import *  # noqa: F403,E402


def analyze_funnel(data):
    """Analyze onboarding funnel for drop-offs and improvement potential."""
    steps = data["steps"]

    if len(steps) < 2:
        return {"error": "Need at least 2 funnel steps"}

    total_start = steps[0]["users"]
    analysis = []
    worst_step = None
    worst_drop = 0

    for i in range(len(steps)):
        step = steps[i]
        users = step["users"]
        rate_from_start = (users / total_start * 100) if total_start > 0 else 0

        if i == 0:
            step_analysis = {
                "step": step["name"],
                "users": users,
                "rate_from_start": round(rate_from_start, 1),
                "drop_rate": 0,
                "dropped_users": 0,
                "is_worst": False
            }
        else:
            prev_users = steps[i - 1]["users"]
            dropped = prev_users - users
            drop_rate = (dropped / prev_users * 100) if prev_users > 0 else 0

            step_analysis = {
                "step": step["name"],
                "users": users,
                "rate_from_start": round(rate_from_start, 1),
                "drop_rate": round(drop_rate, 1),
                "dropped_users": dropped,
                "is_worst": False
            }

            if drop_rate > worst_drop:
                worst_drop = drop_rate
                worst_step = i

        analysis.append(step_analysis)

    if worst_step is not None:
        analysis[worst_step]["is_worst"] = True

    # Calculate improvement potential
    final_users = steps[-1]["users"]
    overall_conversion = (final_users / total_start * 100) if total_start > 0 else 0

    improvements = []
    if worst_step is not None:
        worst = analysis[worst_step]
        # What if we halved the drop-off at the worst step?
        current_drop_rate = worst["drop_rate"] / 100
        improved_drop_rate = current_drop_rate / 2
        prev_users = steps[worst_step - 1]["users"]
        gained_users = int(prev_users * (current_drop_rate - improved_drop_rate))

        # Propagate improvement through remaining steps
        cascade_rate = 1.0
        for j in range(worst_step + 1, len(steps)):
            if steps[j - 1]["users"] > 0:
                cascade_rate *= steps[j]["users"] / steps[j - 1]["users"]

        additional_activated = int(gained_users * cascade_rate)

        improvements.append({
            "action": f"Halve drop-off at '{worst['step']}'",
            "current_drop": f"{worst['drop_rate']}%",
            "target_drop": f"{worst['drop_rate'] / 2:.1f}%",
            "users_saved": gained_users,
            "additional_activated": additional_activated,
            "impact_on_overall": f"+{(additional_activated / total_start * 100):.1f}pp"
        })

    # Score
    score = min(100, max(0, int(overall_conversion * 5)))  # 20% activation = 100
    if overall_conversion < 5:
        score = max(0, int(overall_conversion * 10))

    return {
        "steps": analysis,
        "summary": {
            "total_start": total_start,
            "total_activated": final_users,
            "overall_conversion": round(overall_conversion, 1),
            "worst_step": analysis[worst_step]["step"] if worst_step else None,
            "worst_drop_rate": round(worst_drop, 1),
            "score": score
        },
        "improvements": improvements
    }
