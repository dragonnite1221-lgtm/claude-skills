# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


class LocalizationHelperMixin6:
    def _check_translation_quality(
        self,
        translated_metadata: Dict[str, str],
        target_language: str
    ) -> List[str]:
        """Basic quality checks for translations."""
        issues = []

        # Check for untranslated placeholders
        for field, text in translated_metadata.items():
            if '[' in text or '{' in text or 'TODO' in text.upper():
                issues.append(f"{field} contains placeholder text")

        # Check for excessive punctuation
        for field, text in translated_metadata.items():
            if text.count('!') > 3:
                issues.append(f"{field} has excessive exclamation marks")

        return issues
    def _generate_roi_recommendation(self, payback_months: float) -> str:
        """Generate ROI recommendation."""
        if payback_months <= 3:
            return "Excellent ROI - proceed immediately"
        elif payback_months <= 6:
            return "Good ROI - recommended investment"
        elif payback_months <= 12:
            return "Moderate ROI - consider if strategic market"
        else:
            return "Low ROI - reconsider or focus on higher-priority markets first"
