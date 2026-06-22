# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402


class OKRGeneratorMixin4:
    def _translate_kr_to_product(self, kr: str) -> str:
        """Translate KR to product context"""
        product_terms = {
            'MAU': 'product MAU',
            'growth rate': 'feature adoption rate',
            'CAC': 'product onboarding efficiency',
            'retention': 'product retention',
            'NPS': 'product NPS',
            'ARR': 'product-driven revenue',
            'churn': 'product churn'
        }

        result = kr
        for term, replacement in product_terms.items():
            if term in result:
                result = result.replace(term, replacement)
                break
        return result
    def _translate_to_team(self, objective: str, team: str) -> str:
        """Translate objective to team context"""
        team_focus = {
            'Growth': 'acquisition and activation',
            'Platform': 'infrastructure and reliability',
            'Mobile': 'mobile experience',
            'Data': 'analytics and insights',
            'Engineering': 'technical delivery',
            'Design': 'user experience',
            'Product': 'product strategy'
        }

        focus = team_focus.get(team, 'delivery')
        return f"{objective} through {focus}"
    def _translate_kr_to_team(self, kr: str, team: str) -> str:
        """Translate KR to team context"""
        return f"[{team}] {kr}"
    def _is_relevant_for_team(self, objective: str, team: str) -> bool:
        """Check if objective is relevant for team"""
        keywords = self.team_relevance.get(team, [])
        objective_lower = objective.lower()

        # Platform is always relevant (infrastructure supports everything)
        if team == 'Platform':
            return True

        return any(keyword in objective_lower for keyword in keywords)
