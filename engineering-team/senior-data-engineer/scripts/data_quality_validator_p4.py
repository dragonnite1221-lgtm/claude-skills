# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ColumnProfile, DataProfile  # noqa: F401,E501


class GreatExpectationsGenerator:
    """Generate Great Expectations validation suites"""

    def generate_suite(self, profile: DataProfile) -> Dict:
        """Generate a Great Expectations suite from a data profile"""
        expectations = []

        for col_profile in profile.columns:
            col_expectations = self._generate_column_expectations(col_profile)
            expectations.extend(col_expectations)

        # Table-level expectations
        expectations.append({
            "expectation_type": "expect_table_row_count_to_be_between",
            "kwargs": {
                "min_value": max(1, int(profile.row_count * 0.5)),
                "max_value": int(profile.row_count * 2)
            }
        })

        expectations.append({
            "expectation_type": "expect_table_column_count_to_equal",
            "kwargs": {
                "value": profile.column_count
            }
        })

        suite = {
            "expectation_suite_name": f"{profile.name}_suite",
            "expectations": expectations,
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "generator": "data_quality_validator",
                "source_profile": profile.name
            }
        }

        return suite

    def _generate_column_expectations(self, col_profile: ColumnProfile) -> List[Dict]:
        """Generate expectations for a single column"""
        expectations = []
        col_name = col_profile.name

        # Column exists
        expectations.append({
            "expectation_type": "expect_column_to_exist",
            "kwargs": {"column": col_name}
        })

        # Null percentage
        if col_profile.null_percentage < 1:
            expectations.append({
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": col_name}
            })
        elif col_profile.null_percentage < 50:
            expectations.append({
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {
                    "column": col_name,
                    "mostly": 1 - (col_profile.null_percentage / 100 * 1.5)
                }
            })

        # Uniqueness
        if col_profile.unique_percentage > 99:
            expectations.append({
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": col_name}
            })

        # Type-specific expectations
        if col_profile.data_type == 'integer':
            expectations.append({
                "expectation_type": "expect_column_values_to_be_in_type_list",
                "kwargs": {
                    "column": col_name,
                    "type_list": ["int", "int64", "INTEGER", "BIGINT"]
                }
            })
            if col_profile.min_value is not None:
                expectations.append({
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {
                        "column": col_name,
                        "min_value": col_profile.min_value,
                        "max_value": col_profile.max_value
                    }
                })

        elif col_profile.data_type == 'float':
            expectations.append({
                "expectation_type": "expect_column_values_to_be_in_type_list",
                "kwargs": {
                    "column": col_name,
                    "type_list": ["float", "float64", "FLOAT", "DOUBLE"]
                }
            })
            if col_profile.min_value is not None:
                expectations.append({
                    "expectation_type": "expect_column_values_to_be_between",
                    "kwargs": {
                        "column": col_name,
                        "min_value": col_profile.min_value,
                        "max_value": col_profile.max_value
                    }
                })

        elif col_profile.data_type == 'email':
            expectations.append({
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": col_name,
                    "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                }
            })

        elif col_profile.data_type in ('date_iso', 'date'):
            expectations.append({
                "expectation_type": "expect_column_values_to_match_strftime_format",
                "kwargs": {
                    "column": col_name,
                    "strftime_format": "%Y-%m-%d"
                }
            })

        # String length expectations
        if col_profile.min_length is not None:
            expectations.append({
                "expectation_type": "expect_column_value_lengths_to_be_between",
                "kwargs": {
                    "column": col_name,
                    "min_value": max(1, col_profile.min_length),
                    "max_value": col_profile.max_length * 2 if col_profile.max_length else None
                }
            })

        # Categorical (low cardinality) columns
        if col_profile.unique_count <= 20 and col_profile.unique_percentage < 10:
            top_values = [v[0] for v in col_profile.top_values if v[1] > col_profile.total_count * 0.01]
            if top_values:
                expectations.append({
                    "expectation_type": "expect_column_values_to_be_in_set",
                    "kwargs": {
                        "column": col_name,
                        "value_set": top_values,
                        "mostly": 0.95
                    }
                })

        return expectations
