# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from keyword_analyzer_base import *  # noqa: F403,E402


class KeywordAnalyzerMixin2:
    def extract_keywords_from_text(
        self,
        text: str,
        min_word_length: int = 3
    ) -> List[Tuple[str, int]]:
        """
        Extract potential keywords from text (descriptions, reviews).

        Args:
            text: Text to analyze
            min_word_length: Minimum word length to consider

        Returns:
            List of (keyword, frequency) tuples
        """
        # Clean and normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)

        # Extract words
        words = text.split()

        # Filter by length
        words = [w for w in words if len(w) >= min_word_length]

        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have',
            'but', 'not', 'you', 'all', 'can', 'are', 'was', 'were', 'been'
        }
        words = [w for w in words if w not in stop_words]

        # Count frequency
        word_counts = Counter(words)

        # Extract 2-word phrases
        phrases = []
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            phrases.append(phrase)

        phrase_counts = Counter(phrases)

        # Combine and sort
        all_keywords = list(word_counts.items()) + list(phrase_counts.items())
        all_keywords.sort(key=lambda x: x[1], reverse=True)

        return all_keywords[:50]  # Top 50
    def calculate_keyword_density(
        self,
        text: str,
        target_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Calculate keyword density in text.

        Args:
            text: Text to analyze (title, description)
            target_keywords: Keywords to check density for

        Returns:
            Dictionary of keyword: density (percentage)
        """
        text_lower = text.lower()
        total_words = len(text_lower.split())

        densities = {}
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            occurrences = text_lower.count(keyword_lower)
            density = (occurrences / total_words) * 100 if total_words > 0 else 0
            densities[keyword] = round(density, 2)

        return densities
    def _calculate_competition_level(self, competing_apps: int) -> str:
        """Determine competition level based on number of competing apps."""
        if competing_apps < self.COMPETITION_THRESHOLDS['low']:
            return 'low'
        elif competing_apps < self.COMPETITION_THRESHOLDS['medium']:
            return 'medium'
        elif competing_apps < self.COMPETITION_THRESHOLDS['high']:
            return 'high'
        else:
            return 'very_high'
    def _categorize_search_volume(self, search_volume: int) -> str:
        """Categorize search volume."""
        if search_volume < self.VOLUME_CATEGORIES['very_low']:
            return 'very_low'
        elif search_volume < self.VOLUME_CATEGORIES['low']:
            return 'low'
        elif search_volume < self.VOLUME_CATEGORIES['medium']:
            return 'medium'
        elif search_volume < self.VOLUME_CATEGORIES['high']:
            return 'high'
        else:
            return 'very_high'
