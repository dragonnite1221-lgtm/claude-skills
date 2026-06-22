# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import DataProfile, QualityScore, ValidationResult  # noqa: F401,E501


class QualityScoreCalculator:
    """Calculate overall data quality scores"""

    def calculate(self, profile: DataProfile, validation_results: List[ValidationResult]) -> QualityScore:
        """Calculate quality score from profile and validation results"""
        # Completeness: average non-null percentage
        completeness = 100 - statistics.mean([c.null_percentage for c in profile.columns]) if profile.columns else 0

        # Uniqueness: average unique percentage for columns expected to be unique
        unique_cols = [c for c in profile.columns if c.unique_percentage > 90]
        uniqueness = statistics.mean([c.unique_percentage for c in unique_cols]) if unique_cols else 100

        # Validity: percentage of passed checks
        total_checks = len(validation_results)
        passed_checks = sum(1 for r in validation_results if r.passed)
        validity = (passed_checks / total_checks * 100) if total_checks > 0 else 100

        # Consistency: percentage of non-error results
        error_checks = sum(1 for r in validation_results if not r.passed and r.severity == "error")
        consistency = ((total_checks - error_checks) / total_checks * 100) if total_checks > 0 else 100

        # Accuracy: based on pattern matching and type detection
        pattern_detected = sum(1 for c in profile.columns if c.detected_pattern)
        accuracy = min(100, 50 + (pattern_detected / len(profile.columns) * 50)) if profile.columns else 50

        # Overall: weighted average
        overall = (
            completeness * 0.25 +
            uniqueness * 0.15 +
            validity * 0.30 +
            consistency * 0.20 +
            accuracy * 0.10
        )

        return QualityScore(
            completeness=round(completeness, 2),
            uniqueness=round(uniqueness, 2),
            validity=round(validity, 2),
            consistency=round(consistency, 2),
            accuracy=round(accuracy, 2),
            overall=round(overall, 2)
        )
