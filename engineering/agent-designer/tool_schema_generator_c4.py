# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ErrorSpec, ParameterSpec, ToolDescription  # noqa: F401,E501


class ToolSchemaGeneratorMixin4:
    def generate_anthropic_schema(self, description: ToolDescription, input_params: List[ParameterSpec]) -> Dict[str, Any]:
        """Generate Anthropic tool use schema"""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in input_params:
            prop_def = {
                "type": param.type.value,
                "description": param.description
            }
            
            # Add validation rules (Anthropic uses subset of JSON Schema)
            if param.validation_rules:
                # Filter to supported validation rules
                supported_rules = ["minLength", "maxLength", "minimum", "maximum", "pattern", "enum", "items"]
                for rule, value in param.validation_rules.items():
                    if rule in supported_rules:
                        prop_def[rule] = value
            
            input_schema["properties"][param.name] = prop_def
            
            if param.required:
                input_schema["required"].append(param.name)
        
        schema = {
            "name": description.name,
            "description": description.purpose,
            "input_schema": input_schema
        }
        
        return schema
    def generate_error_responses(self, description: ToolDescription) -> List[ErrorSpec]:
        """Generate error response specifications"""
        error_specs = []
        
        # Common errors
        common_errors = [
            {
                "error_code": "invalid_input",
                "error_message": "Invalid input parameters provided",
                "http_status": 400,
                "details": {"validation_errors": []}
            },
            {
                "error_code": "authentication_required",
                "error_message": "Authentication required to access this tool",
                "http_status": 401
            },
            {
                "error_code": "insufficient_permissions",
                "error_message": "Insufficient permissions to perform this operation",
                "http_status": 403
            },
            {
                "error_code": "rate_limit_exceeded",
                "error_message": "Rate limit exceeded. Please try again later",
                "http_status": 429,
                "retry_after": 60
            },
            {
                "error_code": "internal_error",
                "error_message": "Internal server error occurred",
                "http_status": 500
            },
            {
                "error_code": "service_unavailable",
                "error_message": "Service temporarily unavailable",
                "http_status": 503,
                "retry_after": 300
            }
        ]
        
        # Add common errors
        for error in common_errors:
            error_specs.append(ErrorSpec(**error))
        
        # Add tool-specific errors based on error conditions
        for condition in description.error_conditions:
            if "not found" in condition.lower():
                error_specs.append(ErrorSpec(
                    error_code="resource_not_found",
                    error_message=f"Requested resource not found: {condition}",
                    http_status=404
                ))
            elif "timeout" in condition.lower():
                error_specs.append(ErrorSpec(
                    error_code="operation_timeout",
                    error_message=f"Operation timed out: {condition}",
                    http_status=408,
                    retry_after=30
                ))
            elif "quota" in condition.lower() or "limit" in condition.lower():
                error_specs.append(ErrorSpec(
                    error_code="quota_exceeded",
                    error_message=f"Quota or limit exceeded: {condition}",
                    http_status=429,
                    retry_after=3600
                ))
            elif "dependency" in condition.lower():
                error_specs.append(ErrorSpec(
                    error_code="dependency_failure",
                    error_message=f"Dependency service failure: {condition}",
                    http_status=502
                ))
        
        return error_specs
