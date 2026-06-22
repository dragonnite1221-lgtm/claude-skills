# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ColumnSchema, ValidationResult  # noqa: F401,E501


class SchemaValidatorMixin1:
    def _validate_column(self, data: List[Dict], col_schema: ColumnSchema) -> List[ValidationResult]:
        results = []
        col_name = col_schema.name

        # Check column exists
        if data and col_name not in data[0]:
            results.append(ValidationResult(
                check_name="column_exists",
                column=col_name,
                passed=False,
                expected="column present",
                actual="column missing",
                severity="error",
                message=f"Column '{col_name}' not found in data"
            ))
            return results

        values = [row.get(col_name) for row in data]
        failed_rows = []

        # Null check
        null_count = sum(1 for v in values if v is None or v == '')
        if not col_schema.nullable and null_count > 0:
            failed_rows = [i for i, v in enumerate(values) if v is None or v == '']
            results.append(ValidationResult(
                check_name="not_null",
                column=col_name,
                passed=False,
                expected="no nulls",
                actual=f"{null_count} nulls",
                severity="error",
                message=f"Column '{col_name}' has {null_count} null values but is not nullable",
                failed_rows=failed_rows[:100]  # Limit to first 100
            ))

        non_null_values = [v for v in values if v is not None and v != '']

        # Uniqueness check
        if col_schema.unique and non_null_values:
            unique_count = len(set(non_null_values))
            if unique_count != len(non_null_values):
                duplicate_values = [v for v, count in Counter(non_null_values).items() if count > 1]
                results.append(ValidationResult(
                    check_name="unique",
                    column=col_name,
                    passed=False,
                    expected="all unique",
                    actual=f"{len(non_null_values) - unique_count} duplicates",
                    severity="error",
                    message=f"Column '{col_name}' has duplicate values: {duplicate_values[:5]}"
                ))

        # Type validation
        type_failures = self._validate_type(non_null_values, col_schema.data_type)
        if type_failures:
            results.append(ValidationResult(
                check_name="data_type",
                column=col_name,
                passed=False,
                expected=col_schema.data_type,
                actual=f"{len(type_failures)} invalid values",
                severity="error",
                message=f"Column '{col_name}' has {len(type_failures)} values not matching type {col_schema.data_type}",
                failed_rows=type_failures[:100]
            ))

        # Range validation for numeric columns
        if col_schema.min_value is not None or col_schema.max_value is not None:
            range_failures = self._validate_range(non_null_values, col_schema)
            if range_failures:
                results.append(ValidationResult(
                    check_name="value_range",
                    column=col_name,
                    passed=False,
                    expected=f"[{col_schema.min_value}, {col_schema.max_value}]",
                    actual=f"{len(range_failures)} out of range",
                    severity="error",
                    message=f"Column '{col_name}' has values outside range",
                    failed_rows=range_failures[:100]
                ))

        # Length validation for string columns
        if col_schema.min_length is not None or col_schema.max_length is not None:
            length_failures = self._validate_length(non_null_values, col_schema)
            if length_failures:
                results.append(ValidationResult(
                    check_name="string_length",
                    column=col_name,
                    passed=False,
                    expected=f"length [{col_schema.min_length}, {col_schema.max_length}]",
                    actual=f"{len(length_failures)} out of range",
                    severity="warning",
                    message=f"Column '{col_name}' has values with invalid length",
                    failed_rows=length_failures[:100]
                ))

        # Pattern validation
        if col_schema.pattern:
            pattern_failures = self._validate_pattern(non_null_values, col_schema.pattern)
            if pattern_failures:
                results.append(ValidationResult(
                    check_name="pattern_match",
                    column=col_name,
                    passed=False,
                    expected=f"matches {col_schema.pattern}",
                    actual=f"{len(pattern_failures)} non-matching",
                    severity="error",
                    message=f"Column '{col_name}' has values not matching pattern",
                    failed_rows=pattern_failures[:100]
                ))

        # Allowed values validation
        if col_schema.allowed_values:
            allowed_set = set(col_schema.allowed_values)
            invalid = [i for i, v in enumerate(non_null_values) if str(v) not in allowed_set]
            if invalid:
                results.append(ValidationResult(
                    check_name="allowed_values",
                    column=col_name,
                    passed=False,
                    expected=f"one of {col_schema.allowed_values}",
                    actual=f"{len(invalid)} invalid values",
                    severity="error",
                    message=f"Column '{col_name}' has values not in allowed list",
                    failed_rows=invalid[:100]
                ))

        return results
