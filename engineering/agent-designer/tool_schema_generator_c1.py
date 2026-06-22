# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ParameterSpec, ParameterType  # noqa: F401,E501


class ToolSchemaGeneratorMixin1:
    def _parse_parameter_spec(self, param_spec: Dict[str, Any]) -> ParameterSpec:
        """Parse individual parameter specification"""
        name = param_spec.get("name", "")
        type_str = param_spec.get("type", "string")
        description = param_spec.get("description", "")
        required = param_spec.get("required", False)
        default = param_spec.get("default")
        examples = param_spec.get("examples", [])
        
        # Parse parameter type
        param_type = self._parse_parameter_type(type_str)
        
        # Generate validation rules
        validation_rules = self._generate_validation_rules(param_spec, param_type)
        
        return ParameterSpec(
            name=name,
            type=param_type,
            description=description,
            required=required,
            default=default,
            validation_rules=validation_rules,
            examples=examples
        )
    def _parse_parameter_type(self, type_str: str) -> ParameterType:
        """Parse parameter type from string"""
        type_mapping = {
            "str": ParameterType.STRING,
            "string": ParameterType.STRING,
            "text": ParameterType.STRING,
            "int": ParameterType.INTEGER,
            "integer": ParameterType.INTEGER,
            "float": ParameterType.NUMBER,
            "number": ParameterType.NUMBER,
            "bool": ParameterType.BOOLEAN,
            "boolean": ParameterType.BOOLEAN,
            "list": ParameterType.ARRAY,
            "array": ParameterType.ARRAY,
            "dict": ParameterType.OBJECT,
            "object": ParameterType.OBJECT,
            "null": ParameterType.NULL,
            "none": ParameterType.NULL
        }
        
        return type_mapping.get(type_str.lower(), ParameterType.STRING)
    def _generate_validation_rules(self, param_spec: Dict[str, Any], param_type: ParameterType) -> Dict[str, Any]:
        """Generate validation rules for a parameter"""
        rules = {}
        
        # Type-specific validation
        if param_type == ParameterType.STRING:
            rules.update(self._generate_string_validation(param_spec))
        elif param_type == ParameterType.INTEGER:
            rules.update(self._generate_integer_validation(param_spec))
        elif param_type == ParameterType.NUMBER:
            rules.update(self._generate_number_validation(param_spec))
        elif param_type == ParameterType.ARRAY:
            rules.update(self._generate_array_validation(param_spec))
        elif param_type == ParameterType.OBJECT:
            rules.update(self._generate_object_validation(param_spec))
        
        # Common validation rules
        if param_spec.get("required", False):
            rules["required"] = True
        
        if "enum" in param_spec:
            rules["enum"] = param_spec["enum"]
        
        if "pattern" in param_spec:
            rules["pattern"] = param_spec["pattern"]
        elif self._detect_format(param_spec.get("name", ""), param_spec.get("description", "")):
            format_name = self._detect_format(param_spec.get("name", ""), param_spec.get("description", ""))
            if format_name in self.format_validators:
                rules.update(self.format_validators[format_name])
        
        return rules
