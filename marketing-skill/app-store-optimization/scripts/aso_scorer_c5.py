# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


class ASOScorerMixin5:
    def _identify_strengths(self, score_breakdown: Dict[str, Any]) -> List[str]:
        """Identify areas of strength (scores >= 75)."""
        strengths = []

        for category, data in score_breakdown.items():
            if data['score'] >= 75:
                strengths.append(
                    f"{category.replace('_', ' ').title()}: {data['score']}/100"
                )

        return strengths if strengths else ["Focus on building strengths across all areas"]
    def _identify_weaknesses(self, score_breakdown: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement (scores < 60)."""
        weaknesses = []

        for category, data in score_breakdown.items():
            if data['score'] < 60:
                weaknesses.append(
                    f"{category.replace('_', ' ').title()}: {data['score']}/100 - needs improvement"
                )

        return weaknesses if weaknesses else ["All areas performing adequately"]
