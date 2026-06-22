# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import DataProfile, QualityScore, ValidationResult  # noqa: F401,E501


class ReportGenerator:
    """Generate validation reports"""

    def generate_text_report(self,
                            profile: DataProfile,
                            results: List[ValidationResult],
                            score: QualityScore) -> str:
        """Generate a text report"""
        lines = []
        lines.append("=" * 80)
        lines.append("DATA QUALITY VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nDataset: {profile.name}")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Rows: {profile.row_count:,}")
        lines.append(f"Columns: {profile.column_count}")
        lines.append(f"Duplicate Rows: {profile.duplicate_rows:,}")

        # Quality Score
        lines.append("\n" + "-" * 40)
        lines.append("QUALITY SCORES")
        lines.append("-" * 40)
        lines.append(f"  Overall:      {score.overall:>6.1f}% {'✓' if score.overall >= 80 else '✗'}")
        lines.append(f"  Completeness: {score.completeness:>6.1f}%")
        lines.append(f"  Uniqueness:   {score.uniqueness:>6.1f}%")
        lines.append(f"  Validity:     {score.validity:>6.1f}%")
        lines.append(f"  Consistency:  {score.consistency:>6.1f}%")
        lines.append(f"  Accuracy:     {score.accuracy:>6.1f}%")

        # Validation Results Summary
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        errors = sum(1 for r in results if not r.passed and r.severity == "error")
        warnings = sum(1 for r in results if not r.passed and r.severity == "warning")

        lines.append("\n" + "-" * 40)
        lines.append("VALIDATION SUMMARY")
        lines.append("-" * 40)
        lines.append(f"  Total Checks: {len(results)}")
        lines.append(f"  Passed:       {passed} ✓")
        lines.append(f"  Failed:       {failed} ✗")
        lines.append(f"    Errors:     {errors}")
        lines.append(f"    Warnings:   {warnings}")

        # Failed checks details
        if failed > 0:
            lines.append("\n" + "-" * 40)
            lines.append("FAILED CHECKS")
            lines.append("-" * 40)

            for r in results:
                if not r.passed:
                    severity_icon = "❌" if r.severity == "error" else "⚠️"
                    col_str = f"[{r.column}]" if r.column else ""
                    lines.append(f"\n{severity_icon} {r.check_name} {col_str}")
                    lines.append(f"   Expected: {r.expected}")
                    lines.append(f"   Actual:   {r.actual}")
                    if r.message:
                        lines.append(f"   Message:  {r.message}")

        # Column profiles
        lines.append("\n" + "-" * 40)
        lines.append("COLUMN PROFILES")
        lines.append("-" * 40)

        for col in profile.columns:
            lines.append(f"\n  {col.name}")
            lines.append(f"    Type: {col.data_type}")
            lines.append(f"    Nulls: {col.null_count:,} ({col.null_percentage:.1f}%)")
            lines.append(f"    Unique: {col.unique_count:,} ({col.unique_percentage:.1f}%)")

            if col.min_value is not None:
                lines.append(f"    Range: [{col.min_value:.2f}, {col.max_value:.2f}]")
                lines.append(f"    Mean: {col.mean:.2f}, Median: {col.median:.2f}")

            if col.min_length is not None:
                lines.append(f"    Length: [{col.min_length}, {col.max_length}] (avg: {col.avg_length:.1f})")

            if col.detected_pattern:
                lines.append(f"    Pattern: {col.detected_pattern}")

            if col.top_values:
                top_3 = col.top_values[:3]
                lines.append(f"    Top values: {', '.join(f'{v[0]} ({v[1]})' for v in top_3)}")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)

    def generate_json_report(self,
                            profile: DataProfile,
                            results: List[ValidationResult],
                            score: QualityScore) -> Dict:
        """Generate a JSON report"""
        return {
            "report_type": "data_quality_validation",
            "generated_at": datetime.now().isoformat(),
            "dataset": {
                "name": profile.name,
                "row_count": profile.row_count,
                "column_count": profile.column_count,
                "duplicate_rows": profile.duplicate_rows,
                "memory_bytes": profile.memory_size_bytes
            },
            "quality_score": asdict(score),
            "validation_summary": {
                "total_checks": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
                "errors": sum(1 for r in results if not r.passed and r.severity == "error"),
                "warnings": sum(1 for r in results if not r.passed and r.severity == "warning")
            },
            "validation_results": [
                {
                    "check": r.check_name,
                    "column": r.column,
                    "passed": r.passed,
                    "severity": r.severity,
                    "expected": str(r.expected),
                    "actual": str(r.actual),
                    "message": r.message
                }
                for r in results
            ],
            "column_profiles": [asdict(c) for c in profile.columns]
        }
