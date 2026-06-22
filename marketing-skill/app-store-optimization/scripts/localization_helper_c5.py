# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin5:
    def _prioritize_implementation(self, markets: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Create phased implementation plan."""
        phases = []

        # Phase 1: Top revenue markets
        phase_1 = [m for m in markets[:3]]
        if phase_1:
            phases.append({
                'phase': 'Phase 1 (First 30 days)',
                'markets': ', '.join([m['market'] for m in phase_1]),
                'rationale': 'Highest revenue potential markets'
            })

        # Phase 2: Remaining tier 1 and top tier 2
        phase_2 = [m for m in markets[3:6]]
        if phase_2:
            phases.append({
                'phase': 'Phase 2 (Days 31-60)',
                'markets': ', '.join([m['market'] for m in phase_2]),
                'rationale': 'Strong revenue markets with good ROI'
            })

        # Phase 3: Remaining markets
        phase_3 = [m for m in markets[6:]]
        if phase_3:
            phases.append({
                'phase': 'Phase 3 (Days 61-90)',
                'markets': ', '.join([m['market'] for m in phase_3]),
                'rationale': 'Complete global coverage'
            })

        return phases
    def _get_translation_notes(
        self,
        field: str,
        target_language: str,
        estimated_length: int,
        limit: int
    ) -> List[str]:
        """Get translation-specific notes for field."""
        notes = []

        if estimated_length > limit:
            notes.append(f"Condensing required - aim for {limit - 10} characters to allow buffer")

        if field == 'title' and target_language.startswith('zh'):
            notes.append("Chinese characters convey more meaning - may need fewer characters")

        if field == 'keywords' and target_language.startswith('de'):
            notes.append("German compound words may be longer - prioritize shorter keywords")

        return notes
    def _generate_translation_recommendations(
        self,
        target_language: str,
        warnings: List[str]
    ) -> List[str]:
        """Generate translation recommendations."""
        recommendations = [
            "Use professional native speakers for translation",
            "Test translations with local users before finalizing"
        ]

        if warnings:
            recommendations.append("Work with translator to condense text while preserving meaning")

        if target_language.startswith('zh') or target_language.startswith('ja'):
            recommendations.append("Consider cultural context and local idioms")

        return recommendations
    def _get_cultural_keyword_considerations(self, target_market: str) -> Dict[str, List[str]]:
        """Get cultural considerations for keywords by market."""
        # Simplified example - real implementation would be more comprehensive
        considerations = {
            'China': ['Avoid politically sensitive terms', 'Consider local alternatives to blocked services'],
            'Japan': ['Honorific language important', 'Technical terms often use katakana'],
            'Germany': ['Privacy and security terms resonate', 'Efficiency and quality valued'],
            'France': ['French language protection laws', 'Prefer French terms over English'],
            'default': ['Research local search behavior', 'Test with native speakers']
        }

        return considerations.get(target_market, considerations['default'])
    def _get_search_patterns(self, target_market: str) -> List[str]:
        """Get search pattern notes for market."""
        patterns = {
            'China': ['Use both simplified characters and romanization', 'Brand names often romanized'],
            'Japan': ['Mix of kanji, hiragana, and katakana', 'English words common in tech'],
            'Germany': ['Compound words common', 'Specific technical terminology'],
            'default': ['Research local search trends', 'Monitor competitor keywords']
        }

        return patterns.get(target_market, patterns['default'])
    def _determine_adaptation_strategy(self, keyword: str, target_market: str) -> str:
        """Determine how to adapt keyword for market."""
        # Simplified logic
        if target_market in ['China', 'Japan', 'Korea']:
            return 'full_localization'  # Complete translation needed
        elif target_market in ['Germany', 'France', 'Spain']:
            return 'adapt_and_translate'  # Some adaptation needed
        else:
            return 'direct_translation'  # Direct translation usually sufficient
