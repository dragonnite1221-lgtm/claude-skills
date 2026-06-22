# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ParameterSpec, ToolDescription  # noqa: F401,E501


class ToolSchemaGeneratorMixin3:
    def _generate_object_validation(self, param_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object-specific validation rules"""
        rules = {}
        
        if "properties" in param_spec:
            rules["properties"] = param_spec["properties"]
        
        if "required_properties" in param_spec:
            rules["required"] = param_spec["required_properties"]
        
        if "additional_properties" in param_spec:
            rules["additionalProperties"] = param_spec["additional_properties"]
        else:
            rules["additionalProperties"] = False
        
        if "min_properties" in param_spec:
            rules["minProperties"] = param_spec["min_properties"]
        
        if "max_properties" in param_spec:
            rules["maxProperties"] = param_spec["max_properties"]
        
        return rules
    def _detect_format(self, name: str, description: str) -> Optional[str]:
        """Detect parameter format from name and description"""
        combined = (name + " " + description).lower()
        
        format_indicators = {
            "email": ["email", "e-mail", "email_address"],
            "url": ["url", "uri", "link", "website", "endpoint"],
            "uuid": ["uuid", "guid", "identifier", "id"],
            "date": ["date", "birthday", "created_date", "modified_date"],
            "datetime": ["datetime", "timestamp", "created_at", "updated_at"],
            "password": ["password", "secret", "token", "api_key"]
        }
        
        for format_name, indicators in format_indicators.items():
            if any(indicator in combined for indicator in indicators):
                return format_name
        
        return None
    def generate_openai_schema(self, description: ToolDescription, input_params: List[ParameterSpec]) -> Dict[str, Any]:
        """Generate OpenAI function calling schema"""
        properties = {}
        required = []
        
        for param in input_params:
            prop_def = {
                "type": param.type.value,
                "description": param.description
            }
            
            # Add validation rules
            if param.validation_rules:
                prop_def.update(param.validation_rules)
            
            # Add examples
            if param.examples:
                prop_def["examples"] = param.examples
            
            # Add default value
            if param.default is not None:
                prop_def["default"] = param.default
            
            properties[param.name] = prop_def
            
            if param.required:
                required.append(param.name)
        
        schema = {
            "name": description.name,
            "description": description.purpose,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False
            }
        }
        
        return schema
