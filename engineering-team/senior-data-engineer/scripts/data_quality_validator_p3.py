# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ColumnProfile, DataProfile  # noqa: F401,E501
from data_quality_validator_p1 import TypeDetector  # noqa: F401,E501


class DataProfiler:
    """Generate statistical profiles of datasets"""

    def profile(self, data: List[Dict], name: str = "dataset") -> DataProfile:
        """Generate a complete profile of the dataset"""
        if not data:
            return DataProfile(
                name=name,
                row_count=0,
                column_count=0,
                columns=[],
                duplicate_rows=0,
                memory_size_bytes=0,
                profile_timestamp=datetime.now().isoformat()
            )

        columns = list(data[0].keys())
        column_profiles = []

        for col in columns:
            profile = self._profile_column(data, col)
            column_profiles.append(profile)

        # Count duplicates
        row_tuples = [tuple(sorted(row.items())) for row in data]
        duplicate_count = len(row_tuples) - len(set(row_tuples))

        # Estimate memory size
        memory_size = sys.getsizeof(data) + sum(
            sys.getsizeof(row) + sum(sys.getsizeof(v) for v in row.values())
            for row in data
        )

        return DataProfile(
            name=name,
            row_count=len(data),
            column_count=len(columns),
            columns=column_profiles,
            duplicate_rows=duplicate_count,
            memory_size_bytes=memory_size,
            profile_timestamp=datetime.now().isoformat()
        )

    def _profile_column(self, data: List[Dict], column: str) -> ColumnProfile:
        """Generate profile for a single column"""
        values = [row.get(column) for row in data]
        non_null = [v for v in values if v is not None and v != '']

        total_count = len(values)
        null_count = total_count - len(non_null)
        null_pct = (null_count / total_count * 100) if total_count > 0 else 0

        unique_values = set(str(v) for v in non_null)
        unique_count = len(unique_values)
        unique_pct = (unique_count / len(non_null) * 100) if non_null else 0

        # Detect type
        sample = [str(v) for v in non_null[:1000]]
        detected_type = TypeDetector.detect_type(sample)
        detected_pattern = TypeDetector.detect_pattern(sample)

        # Top values
        value_counts = Counter(str(v) for v in non_null)
        top_values = value_counts.most_common(10)

        profile = ColumnProfile(
            name=column,
            data_type=detected_type,
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_pct,
            unique_count=unique_count,
            unique_percentage=unique_pct,
            detected_pattern=detected_pattern,
            top_values=top_values
        )

        # Add numeric stats if applicable
        if detected_type in ('integer', 'float'):
            numeric_values = []
            for v in non_null:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass

            if numeric_values:
                sorted_vals = sorted(numeric_values)
                profile.min_value = min(numeric_values)
                profile.max_value = max(numeric_values)
                profile.mean = statistics.mean(numeric_values)
                profile.median = statistics.median(numeric_values)
                if len(numeric_values) > 1:
                    profile.std_dev = statistics.stdev(numeric_values)
                profile.percentile_25 = sorted_vals[len(sorted_vals) // 4]
                profile.percentile_75 = sorted_vals[(3 * len(sorted_vals)) // 4]

        # Add string stats
        if detected_type == 'string':
            lengths = [len(str(v)) for v in non_null]
            if lengths:
                profile.min_length = min(lengths)
                profile.max_length = max(lengths)
                profile.avg_length = statistics.mean(lengths)

        return profile
