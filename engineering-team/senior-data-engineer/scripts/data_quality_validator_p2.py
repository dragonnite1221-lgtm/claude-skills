# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import DataSchema, ValidationResult  # noqa: F401,E501
from data_quality_validator_p1 import BaseValidator  # noqa: F401,E501


class AnomalyDetector(BaseValidator):
    """Detect anomalies in data"""

    def __init__(self, z_threshold: float = 3.0, iqr_multiplier: float = 1.5):
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier

    def validate(self, data: List[Dict], schema: Optional[DataSchema] = None) -> List[ValidationResult]:
        results = []

        if not data:
            return results

        # Get numeric columns
        numeric_columns = []
        for col in data[0].keys():
            values = [row.get(col) for row in data]
            non_null = [v for v in values if v is not None and v != '']
            try:
                [float(v) for v in non_null[:100]]
                numeric_columns.append(col)
            except (ValueError, TypeError):
                pass

        for col in numeric_columns:
            col_results = self._detect_numeric_anomalies(data, col)
            results.extend(col_results)

        return results

    def _detect_numeric_anomalies(self, data: List[Dict], column: str) -> List[ValidationResult]:
        results = []

        values = []
        for row in data:
            v = row.get(column)
            if v is not None and v != '':
                try:
                    values.append(float(v))
                except (ValueError, TypeError):
                    pass

        if len(values) < 10:
            return results

        # Z-score method
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0

        if std > 0:
            z_outliers = []
            for i, v in enumerate(values):
                z_score = abs((v - mean) / std)
                if z_score > self.z_threshold:
                    z_outliers.append((i, v, z_score))

            if z_outliers:
                results.append(ValidationResult(
                    check_name="z_score_outlier",
                    column=column,
                    passed=len(z_outliers) == 0,
                    expected=f"z-score <= {self.z_threshold}",
                    actual=f"{len(z_outliers)} outliers",
                    severity="warning",
                    message=f"Column '{column}' has {len(z_outliers)} statistical outliers (z-score method)",
                    failed_rows=[o[0] for o in z_outliers[:100]]
                ))

        # IQR method
        sorted_values = sorted(values)
        q1_idx = len(sorted_values) // 4
        q3_idx = (3 * len(sorted_values)) // 4
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1

        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr

        iqr_outliers = [(i, v) for i, v in enumerate(values) if v < lower_bound or v > upper_bound]

        if iqr_outliers:
            results.append(ValidationResult(
                check_name="iqr_outlier",
                column=column,
                passed=len(iqr_outliers) == 0,
                expected=f"value in [{lower_bound:.2f}, {upper_bound:.2f}]",
                actual=f"{len(iqr_outliers)} outliers",
                severity="warning",
                message=f"Column '{column}' has {len(iqr_outliers)} outliers (IQR method)",
                failed_rows=[o[0] for o in iqr_outliers[:100]]
            ))

        return results
