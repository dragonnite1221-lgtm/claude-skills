# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from keyword_analyzer_base import *  # noqa: F403,E402


class KeywordAnalyzerMixin1:
    def compare_keywords(self, keywords_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple keywords and rank by potential.

        Args:
            keywords_data: List of dicts with keyword, search_volume, competing_apps, relevance_score

        Returns:
            Comparison report with ranked keywords
        """
        analyses = []
        for kw_data in keywords_data:
            analysis = self.analyze_keyword(
                keyword=kw_data['keyword'],
                search_volume=kw_data.get('search_volume', 0),
                competing_apps=kw_data.get('competing_apps', 0),
                relevance_score=kw_data.get('relevance_score', 0.0)
            )
            analyses.append(analysis)

        # Sort by potential score (descending)
        ranked_keywords = sorted(
            analyses,
            key=lambda x: x['potential_score'],
            reverse=True
        )

        # Categorize keywords
        primary_keywords = [
            kw for kw in ranked_keywords
            if kw['potential_score'] >= 70 and kw['relevance_score'] >= 0.8
        ]

        secondary_keywords = [
            kw for kw in ranked_keywords
            if 50 <= kw['potential_score'] < 70 and kw['relevance_score'] >= 0.6
        ]

        long_tail_keywords = [
            kw for kw in ranked_keywords
            if kw['is_long_tail'] and kw['relevance_score'] >= 0.7
        ]

        return {
            'total_keywords_analyzed': len(analyses),
            'ranked_keywords': ranked_keywords,
            'primary_keywords': primary_keywords[:5],  # Top 5
            'secondary_keywords': secondary_keywords[:10],  # Top 10
            'long_tail_keywords': long_tail_keywords[:10],  # Top 10
            'summary': self._generate_comparison_summary(
                primary_keywords,
                secondary_keywords,
                long_tail_keywords
            )
        }
    def find_long_tail_opportunities(
        self,
        base_keyword: str,
        modifiers: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate long-tail keyword variations.

        Args:
            base_keyword: Core keyword (e.g., "task manager")
            modifiers: List of modifiers (e.g., ["free", "simple", "team"])

        Returns:
            List of long-tail keyword suggestions
        """
        long_tail_keywords = []

        # Generate combinations
        for modifier in modifiers:
            # Modifier + base
            variation1 = f"{modifier} {base_keyword}"
            long_tail_keywords.append({
                'keyword': variation1,
                'pattern': 'modifier_base',
                'estimated_competition': 'low',
                'rationale': f"Less competitive variation of '{base_keyword}'"
            })

            # Base + modifier
            variation2 = f"{base_keyword} {modifier}"
            long_tail_keywords.append({
                'keyword': variation2,
                'pattern': 'base_modifier',
                'estimated_competition': 'low',
                'rationale': f"Specific use-case variation of '{base_keyword}'"
            })

        # Add question-based long-tail
        question_words = ['how', 'what', 'best', 'top']
        for q_word in question_words:
            question_keyword = f"{q_word} {base_keyword}"
            long_tail_keywords.append({
                'keyword': question_keyword,
                'pattern': 'question_based',
                'estimated_competition': 'very_low',
                'rationale': f"Informational search query"
            })

        return long_tail_keywords
