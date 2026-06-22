# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ParameterSpec, ToolDescription  # noqa: F401,E501


class ToolSchemaGeneratorMixin0:
    """Generate structured tool schemas from descriptions"""
    def __init__(self):
        self.common_patterns = self._define_common_patterns()
        self.format_validators = self._define_format_validators()
        self.security_templates = self._define_security_templates()
    def _define_common_patterns(self) -> Dict[str, str]:
        """Define common regex patterns for validation"""
        return {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "url": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            "phone": r"^\+?1?[0-9]{10,15}$",
            "ip_address": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            "date": r"^\d{4}-\d{2}-\d{2}$",
            "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?$",
            "slug": r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
            "semantic_version": r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        }
    def _define_format_validators(self) -> Dict[str, Dict[str, Any]]:
        """Define format validators for common data types"""
        return {
            "email": {
                "type": "string",
                "format": "email",
                "pattern": self.common_patterns["email"],
                "min_length": 5,
                "max_length": 254
            },
            "url": {
                "type": "string",
                "format": "uri",
                "pattern": self.common_patterns["url"],
                "min_length": 7,
                "max_length": 2048
            },
            "uuid": {
                "type": "string",
                "format": "uuid",
                "pattern": self.common_patterns["uuid"],
                "min_length": 36,
                "max_length": 36
            },
            "date": {
                "type": "string",
                "format": "date",
                "pattern": self.common_patterns["date"],
                "min_length": 10,
                "max_length": 10
            },
            "datetime": {
                "type": "string",
                "format": "date-time",
                "pattern": self.common_patterns["datetime"],
                "min_length": 19,
                "max_length": 30
            },
            "password": {
                "type": "string",
                "min_length": 8,
                "max_length": 128,
                "pattern": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
            }
        }
    def _define_security_templates(self) -> Dict[str, Dict[str, Any]]:
        """Define security requirement templates"""
        return {
            "authentication_required": {
                "requires_auth": True,
                "auth_methods": ["bearer_token", "api_key"],
                "scope_required": ["read", "write"]
            },
            "rate_limited": {
                "rate_limits": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "burst_limit": 10
                }
            },
            "input_sanitization": {
                "sanitize_html": True,
                "validate_sql_injection": True,
                "escape_special_chars": True
            },
            "output_validation": {
                "validate_response_schema": True,
                "filter_sensitive_data": True,
                "content_type_validation": True
            }
        }
    def parse_tool_description(self, description: ToolDescription) -> ParameterSpec:
        """Parse tool description into structured parameters"""
        input_params = []
        output_params = []
        
        # Parse input parameters
        for input_spec in description.inputs:
            param = self._parse_parameter_spec(input_spec)
            input_params.append(param)
        
        # Parse output parameters
        for output_spec in description.outputs:
            param = self._parse_parameter_spec(output_spec)
            output_params.append(param)
        
        return input_params, output_params
