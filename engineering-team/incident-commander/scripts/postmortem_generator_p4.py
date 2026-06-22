# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from postmortem_generator_base import *  # noqa: F403,E402
# fmt: off
from postmortem_generator_p1 import CAT_TO_ACTION, FACTOR_CATEGORIES, IncidentData, MISSING_ACTION_TEMPLATES, THEME_RECS, VERSION  # noqa: E402,E501
from postmortem_generator_p2 import ContributingFactor, FiveWhysAnalysis, TimelineMetrics  # noqa: E402,E501
from postmortem_generator_p3 import ActionItem  # noqa: E402,E501
# fmt: on


class PostmortemReport:
    """Complete postmortem document assembled from all analysis components."""

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw
        self.incident = IncidentData(raw.get("incident", {}))
        self.timeline = TimelineMetrics(raw.get("timeline", {}), self.incident.severity)
        self.resolution: Dict[str, Any] = raw.get("resolution", {})
        self.participants: List[Dict[str, str]] = raw.get("participants", [])
        # Derived analysis
        self.contributing_factors = [ContributingFactor(f, i)
                                     for i, f in enumerate(self.resolution.get("contributing_factors", []))]
        self.five_whys = [FiveWhysAnalysis(f) for f in self.contributing_factors]
        self.action_items = [ActionItem(a) for a in raw.get("action_items", [])]
        self.factor_distribution = self._compute_factor_distribution()
        self.coverage_gaps = self._find_coverage_gaps()
        self.suggested_actions = self._suggest_missing_actions()
        self.theme_recommendations = self._build_theme_recommendations()

    def _compute_factor_distribution(self) -> Dict[str, float]:
        dist: Dict[str, float] = {c: 0.0 for c in FACTOR_CATEGORIES}
        total = sum(f.weight for f in self.contributing_factors) or 1.0
        for f in self.contributing_factors:
            dist[f.category] += f.weight
        return {k: round(v / total * 100, 1) for k, v in dist.items()}

    def _find_coverage_gaps(self) -> List[str]:
        factor_cats = {f.category for f in self.contributing_factors}
        action_types = {a.type for a in self.action_items}
        gaps = []
        for cat in factor_cats:
            expected = CAT_TO_ACTION.get(cat)
            if expected and expected not in action_types:
                gaps.append(f"No '{expected}' action item to address '{cat}' contributing factor")
        return gaps

    def _suggest_missing_actions(self) -> List[Dict[str, str]]:
        factor_cats = {f.category for f in self.contributing_factors}
        action_types = {a.type for a in self.action_items}
        suggestions = []
        for cat in factor_cats:
            expected = CAT_TO_ACTION.get(cat)
            if expected and expected not in action_types:
                suggestions.append({
                    "type": expected,
                    "suggestion": MISSING_ACTION_TEMPLATES.get(expected, "Add an action item for this gap"),
                    "reason": f"No action item addresses the '{cat}' contributing factor"})
        return suggestions

    def _build_theme_recommendations(self) -> Dict[str, List[str]]:
        seen: Dict[str, List[str]] = {}
        for a in self.five_whys:
            if a.systemic_theme not in seen:
                seen[a.systemic_theme] = THEME_RECS.get(a.systemic_theme, [])
        return seen

    def customer_impact_summary(self) -> Dict[str, Any]:
        impact = self.resolution.get("customer_impact", {})
        affected = impact.get("affected_users", 0)
        failed_tx = impact.get("failed_transactions", 0)
        revenue = impact.get("revenue_impact_usd", 0)
        data_loss = impact.get("data_loss", False)
        comm_required = affected > 1000 or data_loss or revenue > 10000
        sev = "high" if (affected > 10000 or revenue > 50000) else (
            "medium" if (affected > 1000 or revenue > 5000) else "low")
        return {"affected_users": affected, "failed_transactions": failed_tx,
                "revenue_impact_usd": revenue, "data_loss": data_loss,
                "data_integrity": "compromised" if data_loss else "intact",
                "customer_communication_required": comm_required, "impact_severity": sev}

    def executive_summary(self) -> str:
        mttr = self.timeline.mttr
        ci = self.customer_impact_summary()
        mttr_str = f"{mttr:.0f} minutes" if mttr is not None else "unknown duration"
        parts = [
            f"On {self._fmt_date(self.timeline.issue_started)}, a {self.incident.severity} "
            f"incident (\"{self.incident.title}\") impacted the {self.incident.service} service.",
            f"The root cause was identified as: {self.resolution.get('root_cause', 'Unknown root cause')}.",
            f"The incident was resolved in {mttr_str}, affecting approximately "
            f"{ci['affected_users']:,} users with an estimated revenue impact of ${ci['revenue_impact_usd']:,.2f}.",
            "Data loss was confirmed; affected customers must be notified." if ci["data_loss"]
            else "No data loss occurred during this incident."]
        return " ".join(parts)

    @staticmethod
    def _fmt_date(dt: Optional[datetime]) -> str:
        return dt.strftime("%Y-%m-%d at %H:%M UTC") if dt else "an unknown date"

    def overdue_p1_items(self) -> List[Dict[str, str]]:
        return [{"title": a.title, "owner": a.owner, "deadline": a.deadline}
                for a in self.action_items if a.priority in ("P0", "P1") and a.is_past_deadline]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": VERSION, "incident": self.incident.to_dict(),
            "executive_summary": self.executive_summary(),
            "timeline_metrics": self.timeline.to_dict(),
            "customer_impact": self.customer_impact_summary(),
            "root_cause": self.resolution.get("root_cause", ""),
            "contributing_factors": [f.to_dict() for f in self.contributing_factors],
            "factor_distribution": self.factor_distribution,
            "five_whys_analysis": [a.to_dict() for a in self.five_whys],
            "theme_recommendations": self.theme_recommendations,
            "mitigation_steps": self.resolution.get("mitigation_steps", []),
            "permanent_fix": self.resolution.get("permanent_fix", ""),
            "action_items": [a.to_dict() for a in self.action_items],
            "action_item_coverage_gaps": self.coverage_gaps,
            "suggested_actions": self.suggested_actions,
            "overdue_p1_items": self.overdue_p1_items(),
            "participants": self.participants}
def _bar(pct: float, width: int = 30) -> str:
    """Render a text-based horizontal bar chart segment."""
    filled = int(round(pct / 100 * width))
    return "[" + "#" * filled + "." * (width - filled) + "]"
