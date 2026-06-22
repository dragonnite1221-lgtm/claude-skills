# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import DataSchema, ValidationResult  # noqa: F401,E501


class TypeDetector:
    """Detect and infer data types from values"""

    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'phone': r'^\+?[\d\s\-\(\)]{10,}$',
        'url': r'^https?://[^\s]+$',
        'ipv4': r'^(\d{1,3}\.){3}\d{1,3}$',
        'date_iso': r'^\d{4}-\d{2}-\d{2}$',
        'datetime_iso': r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
        'credit_card': r'^\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}$',
    }

    @classmethod
    def detect_type(cls, values: List[str]) -> str:
        """Detect the most likely data type from a sample of values"""
        non_empty = [v for v in values if v and v.strip()]
        if not non_empty:
            return "string"

        # Check for patterns first
        for pattern_name, pattern in cls.PATTERNS.items():
            regex = re.compile(pattern, re.IGNORECASE)
            matches = sum(1 for v in non_empty if regex.match(v.strip()))
            if matches / len(non_empty) > 0.9:
                return pattern_name

        # Check for numeric types
        int_count = 0
        float_count = 0
        bool_count = 0

        for v in non_empty:
            v = v.strip()
            if v.lower() in ('true', 'false', 'yes', 'no', '1', '0'):
                bool_count += 1
            try:
                int(v)
                int_count += 1
            except ValueError:
                try:
                    float(v)
                    float_count += 1
                except ValueError:
                    pass

        if bool_count / len(non_empty) > 0.9:
            return "boolean"
        if int_count / len(non_empty) > 0.9:
            return "integer"
        if (int_count + float_count) / len(non_empty) > 0.9:
            return "float"

        return "string"

    @classmethod
    def detect_pattern(cls, values: List[str]) -> Optional[str]:
        """Try to detect a common pattern in string values"""
        non_empty = [v for v in values if v and v.strip()]
        if not non_empty or len(non_empty) < 10:
            return None

        for pattern_name, pattern in cls.PATTERNS.items():
            regex = re.compile(pattern, re.IGNORECASE)
            matches = sum(1 for v in non_empty if regex.match(v.strip()))
            if matches / len(non_empty) > 0.8:
                return pattern_name

        return None


class BaseValidator(ABC):
    """Base class for validators"""

    @abstractmethod
    def validate(self, data: List[Dict], schema: Optional[DataSchema] = None) -> List[ValidationResult]:
        pass
