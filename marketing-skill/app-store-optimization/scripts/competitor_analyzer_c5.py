# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


class CompetitorAnalyzerMixin5:
    def _assess_competitive_position(
        self,
        your_analysis: Dict[str, Any],
        competitor_comparison: Dict[str, Any]
    ) -> str:
        """Assess your competitive position."""
        your_strength = your_analysis['competitive_strength']
        competitors = competitor_comparison['ranked_competitors']

        if not competitors:
            return "No comparison data available"

        # Find where you'd rank
        better_than_count = sum(
            1 for comp in competitors
            if your_strength > comp['competitive_strength']
        )

        position_percentage = (better_than_count / len(competitors)) * 100

        if position_percentage >= 75:
            return "Strong Position: Top quartile in competitive strength"
        elif position_percentage >= 50:
            return "Competitive Position: Above average, opportunities for improvement"
        elif position_percentage >= 25:
            return "Challenging Position: Below average, requires strategic improvements"
        else:
            return "Weak Position: Bottom quartile, major ASO overhaul needed"
