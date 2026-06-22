# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


class CompetitorAnalyzerMixin2:
    def _extract_keyword_strategy(
        self,
        title: str,
        description: str,
        explicit_keywords: List[str]
    ) -> Dict[str, Any]:
        """Extract keyword strategy from metadata."""
        # Extract keywords from title
        title_keywords = [word.lower() for word in title.split() if len(word) > 3]

        # Extract frequently used words from description
        desc_words = re.findall(r'\b\w{4,}\b', description.lower())
        word_freq = Counter(desc_words)
        frequent_words = [word for word, count in word_freq.most_common(15) if count > 2]

        # Combine with explicit keywords
        all_keywords = list(set(title_keywords + frequent_words + explicit_keywords))

        return {
            'primary_keywords': title_keywords,
            'description_keywords': frequent_words[:10],
            'explicit_keywords': explicit_keywords,
            'total_unique_keywords': len(all_keywords),
            'keyword_focus': self._assess_keyword_focus(title_keywords, frequent_words)
        }
    def _assess_rating_quality(self, rating: float, ratings_count: int) -> str:
        """Assess the quality of ratings."""
        if ratings_count < 100:
            return 'insufficient_data'
        elif rating >= 4.5 and ratings_count > 1000:
            return 'excellent'
        elif rating >= 4.0 and ratings_count > 500:
            return 'good'
        elif rating >= 3.5:
            return 'average'
        else:
            return 'poor'
    def _calculate_competitive_strength(
        self,
        rating: float,
        ratings_count: int,
        description_length: int
    ) -> float:
        """
        Calculate overall competitive strength (0-100).

        Factors:
        - Rating quality (40%)
        - Rating volume (30%)
        - Metadata quality (30%)
        """
        # Rating quality score (0-40)
        rating_score = (rating / 5.0) * 40

        # Rating volume score (0-30)
        volume_score = min((ratings_count / 10000) * 30, 30)

        # Metadata quality score (0-30)
        metadata_score = min((description_length / 2000) * 30, 30)

        total_score = rating_score + volume_score + metadata_score

        return round(total_score, 1)
    def _identify_differentiators(self, description: str) -> List[str]:
        """Identify key differentiators from description."""
        differentiator_keywords = [
            'unique', 'only', 'first', 'best', 'leading', 'exclusive',
            'revolutionary', 'innovative', 'patent', 'award'
        ]

        differentiators = []
        sentences = description.split('.')

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in differentiator_keywords):
                differentiators.append(sentence.strip())

        return differentiators[:5]
    def _find_common_keywords(self, all_keywords: List[str]) -> List[str]:
        """Find keywords used by multiple competitors."""
        keyword_counts = Counter(all_keywords)
        # Return keywords used by at least 2 competitors
        common = [kw for kw, count in keyword_counts.items() if count >= 2]
        return sorted(common, key=lambda x: keyword_counts[x], reverse=True)[:20]
