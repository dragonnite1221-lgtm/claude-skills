# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402


class ToolSchemaGeneratorMixin2:
    def _generate_string_validation(self, param_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate string-specific validation rules"""
        rules = {}
        
        if "min_length" in param_spec:
            rules["minLength"] = param_spec["min_length"]
        elif "min_len" in param_spec:
            rules["minLength"] = param_spec["min_len"]
        else:
            # Infer from description
            desc = param_spec.get("description", "").lower()
            if "password" in desc:
                rules["minLength"] = 8
            elif "email" in desc:
                rules["minLength"] = 5
            elif "name" in desc:
                rules["minLength"] = 1
        
        if "max_length" in param_spec:
            rules["maxLength"] = param_spec["max_length"]
        elif "max_len" in param_spec:
            rules["maxLength"] = param_spec["max_len"]
        else:
            # Reasonable defaults
            desc = param_spec.get("description", "").lower()
            if "password" in desc:
                rules["maxLength"] = 128
            elif "email" in desc:
                rules["maxLength"] = 254
            elif "description" in desc or "content" in desc:
                rules["maxLength"] = 10000
            elif "name" in desc or "title" in desc:
                rules["maxLength"] = 255
            else:
                rules["maxLength"] = 1000
        
        return rules
    def _generate_integer_validation(self, param_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate integer-specific validation rules"""
        rules = {}
        
        if "minimum" in param_spec:
            rules["minimum"] = param_spec["minimum"]
        elif "min" in param_spec:
            rules["minimum"] = param_spec["min"]
        else:
            # Infer from context
            name = param_spec.get("name", "").lower()
            desc = param_spec.get("description", "").lower()
            if any(word in name + desc for word in ["count", "quantity", "amount", "size", "limit"]):
                rules["minimum"] = 0
            elif "page" in name + desc:
                rules["minimum"] = 1
            elif "port" in name + desc:
                rules["minimum"] = 1
                rules["maximum"] = 65535
        
        if "maximum" in param_spec:
            rules["maximum"] = param_spec["maximum"]
        elif "max" in param_spec:
            rules["maximum"] = param_spec["max"]
        
        return rules
    def _generate_number_validation(self, param_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate number-specific validation rules"""
        rules = {}
        
        if "minimum" in param_spec:
            rules["minimum"] = param_spec["minimum"]
        if "maximum" in param_spec:
            rules["maximum"] = param_spec["maximum"]
        if "exclusive_minimum" in param_spec:
            rules["exclusiveMinimum"] = param_spec["exclusive_minimum"]
        if "exclusive_maximum" in param_spec:
            rules["exclusiveMaximum"] = param_spec["exclusive_maximum"]
        if "multiple_of" in param_spec:
            rules["multipleOf"] = param_spec["multiple_of"]
        
        return rules
    def _generate_array_validation(self, param_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate array-specific validation rules"""
        rules = {}
        
        if "min_items" in param_spec:
            rules["minItems"] = param_spec["min_items"]
        elif "min_length" in param_spec:
            rules["minItems"] = param_spec["min_length"]
        else:
            rules["minItems"] = 0
        
        if "max_items" in param_spec:
            rules["maxItems"] = param_spec["max_items"]
        elif "max_length" in param_spec:
            rules["maxItems"] = param_spec["max_length"]
        else:
            rules["maxItems"] = 1000  # Reasonable default
        
        if param_spec.get("unique_items", False):
            rules["uniqueItems"] = True
        
        if "item_type" in param_spec:
            rules["items"] = {"type": param_spec["item_type"]}
        
        return rules
