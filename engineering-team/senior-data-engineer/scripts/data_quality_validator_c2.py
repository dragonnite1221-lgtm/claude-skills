# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ColumnSchema, ValidationResult  # noqa: F401,E501
from data_quality_validator_p1 import TypeDetector  # noqa: F401,E501


class SchemaValidatorMixin2:
    def _validate_type(self, values: List[Any], expected_type: str) -> List[int]:
        """Return indices of values that don't match expected type"""
        failures = []

        for i, v in enumerate(values):
            v_str = str(v)
            valid = False

            if expected_type == "integer":
                try:
                    int(v_str)
                    valid = True
                except ValueError:
                    pass
            elif expected_type == "float":
                try:
                    float(v_str)
                    valid = True
                except ValueError:
                    pass
            elif expected_type == "boolean":
                valid = v_str.lower() in ('true', 'false', 'yes', 'no', '1', '0')
            elif expected_type == "email":
                valid = bool(re.match(TypeDetector.PATTERNS['email'], v_str, re.IGNORECASE))
            elif expected_type == "uuid":
                valid = bool(re.match(TypeDetector.PATTERNS['uuid'], v_str, re.IGNORECASE))
            elif expected_type in ("date", "date_iso"):
                valid = bool(re.match(TypeDetector.PATTERNS['date_iso'], v_str))
            elif expected_type in ("datetime", "datetime_iso"):
                valid = bool(re.match(TypeDetector.PATTERNS['datetime_iso'], v_str))
            else:
                valid = True  # string accepts anything

            if not valid:
                failures.append(i)

        return failures
    def _validate_range(self, values: List[Any], col_schema: ColumnSchema) -> List[int]:
        """Return indices of values outside the specified range"""
        failures = []
        for i, v in enumerate(values):
            try:
                num = float(v)
                if col_schema.min_value is not None and num < col_schema.min_value:
                    failures.append(i)
                elif col_schema.max_value is not None and num > col_schema.max_value:
                    failures.append(i)
            except (ValueError, TypeError):
                pass
        return failures
    def _validate_length(self, values: List[Any], col_schema: ColumnSchema) -> List[int]:
        """Return indices of values with invalid string length"""
        failures = []
        for i, v in enumerate(values):
            length = len(str(v))
            if col_schema.min_length is not None and length < col_schema.min_length:
                failures.append(i)
            elif col_schema.max_length is not None and length > col_schema.max_length:
                failures.append(i)
        return failures
    def _validate_pattern(self, values: List[Any], pattern: str) -> List[int]:
        """Return indices of values not matching the pattern"""
        regex = re.compile(pattern)
        return [i for i, v in enumerate(values) if not regex.match(str(v))]
    def _validate_primary_key(self, data: List[Dict], pk_columns: List[str]) -> List[ValidationResult]:
        """Validate primary key uniqueness"""
        results = []
        pk_values = []

        for row in data:
            pk = tuple(row.get(col) for col in pk_columns)
            pk_values.append(pk)

        pk_counts = Counter(pk_values)
        duplicates = {pk: count for pk, count in pk_counts.items() if count > 1}

        if duplicates:
            results.append(ValidationResult(
                check_name="primary_key_unique",
                column=",".join(pk_columns),
                passed=False,
                expected="all unique",
                actual=f"{len(duplicates)} duplicate keys",
                severity="error",
                message=f"Primary key has {len(duplicates)} duplicate combinations"
            ))

        return results
