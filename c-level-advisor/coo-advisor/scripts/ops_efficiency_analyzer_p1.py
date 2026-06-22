# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ops_efficiency_analyzer_base import *  # noqa: F403,E402


ProcessData = dict[str, Any]
TeamData = dict[str, Any]
MetricsData = dict[str, Any]
MATURITY_LEVELS = {
    1: "Ad Hoc",
    2: "Defined",
    3: "Managed",
    4: "Optimized",
    5: "Innovating",
}
MATURITY_DESCRIPTIONS = {
    1: "No documented process. Outcomes depend on individual heroics.",
    2: "Process exists and is documented. Inconsistently followed.",
    3: "Process is followed consistently. Metrics are tracked.",
    4: "Process is optimized based on metrics. Proactively improved.",
    5: "Process enables competitive advantage. Continuously innovating.",
}
MATURITY_CRITERIA = {
    "documentation": {
        "weight": 0.20,
        "levels": {
            0: "No documentation",
            1: "Informal notes or tribal knowledge",
            2: "Process documented but not maintained",
            3: "Documented, current, accessible",
            4: "Documented with examples, edge cases, and owner",
            5: "Living doc with version history and improvement log",
        },
    },
    "ownership": {
        "weight": 0.15,
        "levels": {
            0: "No owner",
            1: "Unclear ownership, multiple people responsible",
            2: "Named team responsible",
            3: "Named individual DRI",
            4: "DRI with metrics accountability",
            5: "DRI with improvement mandate and resources",
        },
    },
    "metrics": {
        "weight": 0.20,
        "levels": {
            0: "No metrics",
            1: "Anecdotal measurement",
            2: "Some metrics tracked, not regularly reviewed",
            3: "Key metrics tracked and reviewed monthly",
            4: "Metrics drive decisions, targets set",
            5: "Predictive metrics, benchmarked externally",
        },
    },
    "automation": {
        "weight": 0.20,
        "levels": {
            0: "100% manual",
            1: "Mostly manual, some tools used",
            2: "Key steps automated, significant manual work remains",
            3: "Majority automated, manual exception handling",
            4: "Mostly automated with exception playbooks",
            5: "Fully automated with human oversight only",
        },
    },
    "consistency": {
        "weight": 0.15,
        "levels": {
            0: "Never consistent",
            1: "Consistent <50% of time",
            2: "Consistent 50-75% of time",
            3: "Consistent 75-90% of time",
            4: "Consistent >90% of time",
            5: "Six Sigma level (>99.7%)",
        },
    },
    "feedback_loop": {
        "weight": 0.10,
        "levels": {
            0: "No feedback loop",
            1: "Ad hoc complaints surface issues",
            2: "Periodic review when problems arise",
            3: "Regular review cadence",
            4: "Structured improvement cycles",
            5: "Real-time feedback with automated triggers",
        },
    },
}
def _get_improvement_action(dimension: str, current_score: int) -> str:
    """Return a concrete improvement action for a given dimension and score."""
    actions = {
        "documentation": {
            0: "Write a basic SOP this week: trigger, steps, owner, done-definition",
            1: "Convert tribal knowledge into a written process doc with clear steps",
            2: "Assign a process owner to maintain and update documentation quarterly",
        },
        "ownership": {
            0: "Assign a DRI (Directly Responsible Individual) today",
            1: "Clarify ownership: assign one named person, remove ambiguity",
            2: "Give the named owner accountability for process metrics",
        },
        "metrics": {
            0: "Define 1-2 metrics that measure if this process is working",
            1: "Set up automated metric collection and add to monthly review",
            2: "Set targets for each metric and review monthly",
        },
        "automation": {
            0: "Identify the highest-volume manual step; automate it first",
            1: "Run automation ROI calc — if payback <12 months, build it",
            2: "Automate exception routing and error notifications",
        },
        "consistency": {
            0: "Root-cause why the process fails; fix the #1 failure mode",
            1: "Create a checklist for the process; require sign-off",
            2: "Add process adherence check to team's weekly review",
        },
        "feedback_loop": {
            0: "Add this process to monthly operational review agenda",
            1: "Create a feedback channel (Slack thread, form) for process issues",
            2: "Set a quarterly review date for this process",
        },
    }
    return actions.get(dimension, {}).get(current_score, "Improve this dimension")
