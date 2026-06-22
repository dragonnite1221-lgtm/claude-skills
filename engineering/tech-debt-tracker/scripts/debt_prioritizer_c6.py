# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402


class DebtPrioritizerMixin6:
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        insights = self._generate_insights()
        
        # Quick wins recommendation
        if insights["quick_wins_count"] > 0:
            recommendations.append(
                f"Start with {insights['quick_wins_count']} quick wins to build momentum "
                "and demonstrate immediate value from tech debt reduction efforts."
            )
        
        # High-risk items
        if insights["high_risk_items_count"] > 5:
            recommendations.append(
                f"Plan careful execution for {insights['high_risk_items_count']} high-risk items. "
                "Consider pair programming, extra testing, and incremental approaches."
            )
        
        # Category focus
        top_category = insights["top_categories_by_effort"][0][0]
        recommendations.append(
            f"Focus initial efforts on '{top_category}' category debt, which represents "
            f"the largest effort investment ({insights['top_categories_by_effort'][0][1]:.1f} hours)."
        )
        
        # Cost of delay urgency
        if insights["average_daily_interest_rate"] > 5:
            recommendations.append(
                f"High average daily interest rate ({insights['average_daily_interest_rate']:.1f}) "
                "suggests urgent action needed. Consider increasing tech debt budget allocation."
            )
        
        # Sprint planning
        sprints_needed = len(self.prioritized_items) / 10  # Rough estimate
        if sprints_needed > 12:
            recommendations.append(
                "Large debt backlog detected. Consider dedicating entire sprints to debt reduction "
                "rather than trying to fit debt work around features."
            )
        
        # Team capacity
        total_effort = insights["total_effort_hours"]
        weeks_needed = total_effort / (self.sprint_capacity_hours * 0.2)
        if weeks_needed > 26:  # Half a year
            recommendations.append(
                f"With current capacity allocation, debt backlog will take {weeks_needed:.0f} weeks. "
                "Consider increasing tech debt budget or focusing on highest-impact items only."
            )
        
        return recommendations
