# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from aso_scorer_base import *  # noqa: F403,E402


class ASOScorerMixin3:
    def score_conversion_metrics(self, conversion: Dict[str, Any]) -> float:
        """
        Score conversion performance (0-100).

        Evaluates:
        - Impression-to-install conversion rate
        - Download velocity
        """
        conversion_rate = conversion.get('impression_to_install', 0.0)
        downloads_30d = conversion.get('downloads_last_30_days', 0)
        downloads_trend = conversion.get('downloads_trend', 'stable')  # 'up', 'stable', 'down'

        # Conversion rate score (0-70 points)
        if conversion_rate >= self.BENCHMARKS['conversion_rate']['target']:
            conversion_score = 70
        elif conversion_rate >= self.BENCHMARKS['conversion_rate']['min']:
            proportion = (conversion_rate - self.BENCHMARKS['conversion_rate']['min']) / \
                        (self.BENCHMARKS['conversion_rate']['target'] - self.BENCHMARKS['conversion_rate']['min'])
            conversion_score = 35 + (proportion * 35)
        else:
            conversion_score = (conversion_rate / self.BENCHMARKS['conversion_rate']['min']) * 35

        # Download velocity score (0-20 points)
        if downloads_30d > 10000:
            velocity_score = 20
        elif downloads_30d > 1000:
            velocity_score = 15
        elif downloads_30d > 100:
            velocity_score = 10
        else:
            velocity_score = 5

        # Trend bonus (0-10 points)
        if downloads_trend == 'up':
            trend_score = 10
        elif downloads_trend == 'stable':
            trend_score = 5
        else:
            trend_score = 0

        total_score = conversion_score + velocity_score + trend_score

        return round(min(total_score, 100), 1)
