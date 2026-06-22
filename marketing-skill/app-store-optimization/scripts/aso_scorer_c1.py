# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


class ASOScorerMixin1:
    def score_metadata_quality(self, metadata: Dict[str, Any]) -> float:
        """
        Score metadata quality (0-100).

        Evaluates:
        - Title optimization
        - Description quality
        - Keyword usage
        """
        scores = []

        # Title score (0-35 points)
        title_keywords = metadata.get('title_keyword_count', 0)
        title_length = metadata.get('title_length', 0)

        title_score = 0
        if title_keywords >= self.BENCHMARKS['title_keyword_usage']['target']:
            title_score = 35
        elif title_keywords >= self.BENCHMARKS['title_keyword_usage']['min']:
            title_score = 25
        else:
            title_score = 10

        # Adjust for title length usage
        if title_length > 25:  # Using most of available space
            title_score += 0
        else:
            title_score -= 5

        scores.append(min(title_score, 35))

        # Description score (0-35 points)
        desc_length = metadata.get('description_length', 0)
        desc_quality = metadata.get('description_quality', 0.0)  # 0-1 scale

        desc_score = 0
        if desc_length >= self.BENCHMARKS['description_length']['target']:
            desc_score = 25
        elif desc_length >= self.BENCHMARKS['description_length']['min']:
            desc_score = 15
        else:
            desc_score = 5

        # Add quality bonus
        desc_score += desc_quality * 10
        scores.append(min(desc_score, 35))

        # Keyword density score (0-30 points)
        keyword_density = metadata.get('keyword_density', 0.0)

        if self.BENCHMARKS['keyword_density']['min'] <= keyword_density <= self.BENCHMARKS['keyword_density']['optimal']:
            density_score = 30
        elif keyword_density < self.BENCHMARKS['keyword_density']['min']:
            # Too low - proportional scoring
            density_score = (keyword_density / self.BENCHMARKS['keyword_density']['min']) * 20
        else:
            # Too high (keyword stuffing) - penalty
            excess = keyword_density - self.BENCHMARKS['keyword_density']['optimal']
            density_score = max(30 - (excess * 5), 0)

        scores.append(density_score)

        return round(sum(scores), 1)
