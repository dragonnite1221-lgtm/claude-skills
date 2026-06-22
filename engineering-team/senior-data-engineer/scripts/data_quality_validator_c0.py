# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import DataSchema, ValidationResult  # noqa: F401,E501


class SchemaValidatorMixin0:
    """Validate data against a schema"""
    def validate(self, data: List[Dict], schema: DataSchema) -> List[ValidationResult]:
        results = []

        if not data:
            results.append(ValidationResult(
                check_name="data_not_empty",
                column=None,
                passed=False,
                expected="non-empty dataset",
                actual="empty dataset",
                severity="error",
                message="Dataset is empty"
            ))
            return results

        # Validate row count
        row_count = len(data)
        if schema.row_count_min and row_count < schema.row_count_min:
            results.append(ValidationResult(
                check_name="row_count_min",
                column=None,
                passed=False,
                expected=f">= {schema.row_count_min}",
                actual=row_count,
                severity="error",
                message=f"Row count {row_count} is below minimum {schema.row_count_min}"
            ))

        if schema.row_count_max and row_count > schema.row_count_max:
            results.append(ValidationResult(
                check_name="row_count_max",
                column=None,
                passed=False,
                expected=f"<= {schema.row_count_max}",
                actual=row_count,
                severity="warning",
                message=f"Row count {row_count} exceeds maximum {schema.row_count_max}"
            ))

        # Validate each column
        for col_schema in schema.columns:
            col_results = self._validate_column(data, col_schema)
            results.extend(col_results)

        # Validate primary key uniqueness
        if schema.primary_key:
            pk_results = self._validate_primary_key(data, schema.primary_key)
            results.extend(pk_results)

        return results
