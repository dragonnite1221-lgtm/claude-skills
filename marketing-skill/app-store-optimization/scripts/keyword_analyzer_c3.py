# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from keyword_analyzer_base import *  # noqa: F403,E402


class KeywordAnalyzerMixin3:
    def _calculate_keyword_difficulty(
        self,
        search_volume: int,
        competing_apps: int
    ) -> float:
        """
        Calculate keyword difficulty score (0-100).
        Higher score = harder to rank.
        """
        if competing_apps == 0:
            return 0.0

        # Competition factor (0-1)
        competition_factor = min(competing_apps / 50000, 1.0)

        # Volume factor (0-1) - higher volume = more difficulty
        volume_factor = min(search_volume / 1000000, 1.0)

        # Difficulty score (weighted average)
        difficulty = (competition_factor * 0.7 + volume_factor * 0.3) * 100

        return round(difficulty, 1)
    def _calculate_potential_score(
        self,
        search_volume: int,
        competing_apps: int,
        relevance_score: float
    ) -> float:
        """
        Calculate overall keyword potential (0-100).
        Higher score = better opportunity.
        """
        # Volume score (0-40 points)
        volume_score = min((search_volume / 100000) * 40, 40)

        # Competition score (0-30 points) - inverse relationship
        if competing_apps > 0:
            competition_score = max(30 - (competing_apps / 500), 0)
        else:
            competition_score = 30

        # Relevance score (0-30 points)
        relevance_points = relevance_score * 30

        total_score = volume_score + competition_score + relevance_points

        return round(min(total_score, 100), 1)
    def _generate_recommendation(
        self,
        potential_score: float,
        difficulty_score: float,
        relevance_score: float
    ) -> str:
        """Generate actionable recommendation for keyword."""
        if relevance_score < 0.5:
            return "Low relevance - avoid targeting"

        if potential_score >= 70:
            return "High priority - target immediately"
        elif potential_score >= 50:
            if difficulty_score < 50:
                return "Good opportunity - include in metadata"
            else:
                return "Competitive - use in description, not title"
        elif potential_score >= 30:
            return "Secondary keyword - use for long-tail variations"
        else:
            return "Low potential - deprioritize"
    def _generate_comparison_summary(
        self,
        primary_keywords: List[Dict[str, Any]],
        secondary_keywords: List[Dict[str, Any]],
        long_tail_keywords: List[Dict[str, Any]]
    ) -> str:
        """Generate summary of keyword comparison."""
        summary_parts = []

        summary_parts.append(
            f"Identified {len(primary_keywords)} high-priority primary keywords."
        )

        if primary_keywords:
            top_keyword = primary_keywords[0]['keyword']
            summary_parts.append(
                f"Top recommendation: '{top_keyword}' (potential score: {primary_keywords[0]['potential_score']})."
            )

        summary_parts.append(
            f"Found {len(secondary_keywords)} secondary keywords for description and metadata."
        )

        summary_parts.append(
            f"Discovered {len(long_tail_keywords)} long-tail opportunities with lower competition."
        )

        return " ".join(summary_parts)
