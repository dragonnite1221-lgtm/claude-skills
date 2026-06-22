# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402


class ParameterType(Enum):
    """Parameter types for tool schemas"""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


class ValidationRule(Enum):
    """Validation rule types"""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    ENUM = "enum"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    MIN_ITEMS = "min_items"
    MAX_ITEMS = "max_items"
    UNIQUE_ITEMS = "unique_items"
    FORMAT = "format"


@dataclass
class ParameterSpec:
    """Parameter specification for tool inputs/outputs"""
    name: str
    type: ParameterType
    description: str
    required: bool = False
    default: Any = None
    validation_rules: Dict[str, Any] = None
    examples: List[Any] = None
    deprecated: bool = False


@dataclass
class ErrorSpec:
    """Error specification for tool responses"""
    error_code: str
    error_message: str
    http_status: int
    retry_after: Optional[int] = None
    details: Dict[str, Any] = None


@dataclass
class RateLimitSpec:
    """Rate limiting specification"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    cooldown_period: int
    rate_limit_key: str = "user_id"


@dataclass
class ToolDescription:
    """Input tool description"""
    name: str
    purpose: str
    category: str
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    error_conditions: List[str]
    side_effects: List[str]
    idempotent: bool
    rate_limits: Dict[str, Any]
    dependencies: List[str]
    examples: List[Dict[str, Any]]
    security_requirements: List[str]


@dataclass
class ToolSchema:
    """Complete tool schema with validation and examples"""
    name: str
    description: str
    openai_schema: Dict[str, Any]
    anthropic_schema: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]
    error_responses: List[ErrorSpec]
    rate_limits: RateLimitSpec
    examples: List[Dict[str, Any]]
    metadata: Dict[str, Any]
