# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from review_analyzer_base import *  # noqa: F403,E402


class ReviewAnalyzerMixin1:
    def extract_common_themes(
        self,
        reviews: List[Dict[str, Any]],
        min_mentions: int = 3
    ) -> Dict[str, Any]:
        """
        Extract frequently mentioned themes and topics.

        Args:
            reviews: List of review dicts
            min_mentions: Minimum mentions to be considered common

        Returns:
            Common themes analysis
        """
        # Extract all words from reviews
        all_words = []
        all_phrases = []

        for review in reviews:
            text = review.get('text', '').lower()
            # Clean text
            text = re.sub(r'[^\w\s]', ' ', text)
            words = text.split()

            # Filter out common words
            stop_words = {
                'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have',
                'app', 'apps', 'very', 'really', 'just', 'but', 'not', 'you'
            }
            words = [w for w in words if w not in stop_words and len(w) > 3]

            all_words.extend(words)

            # Extract 2-3 word phrases
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                all_phrases.append(phrase)

        # Count frequency
        word_freq = Counter(all_words)
        phrase_freq = Counter(all_phrases)

        # Filter by min_mentions
        common_words = [
            {'word': word, 'mentions': count}
            for word, count in word_freq.most_common(30)
            if count >= min_mentions
        ]

        common_phrases = [
            {'phrase': phrase, 'mentions': count}
            for phrase, count in phrase_freq.most_common(20)
            if count >= min_mentions
        ]

        # Categorize themes
        themes = self._categorize_themes(common_words, common_phrases)

        return {
            'common_words': common_words,
            'common_phrases': common_phrases,
            'identified_themes': themes,
            'insights': self._generate_theme_insights(themes)
        }
