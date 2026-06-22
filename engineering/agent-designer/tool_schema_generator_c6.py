# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ParameterSpec, ParameterType, ToolDescription  # noqa: F401,E501


class ToolSchemaGeneratorMixin6:
    def _generate_example_value(self, param: ParameterSpec) -> Any:
        """Generate example value for a parameter"""
        if param.type == ParameterType.STRING:
            format_examples = {
                "email": "user@example.com",
                "url": "https://example.com",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2024-01-15",
                "datetime": "2024-01-15T10:30:00Z"
            }
            
            # Check for format in validation rules
            if param.validation_rules and "format" in param.validation_rules:
                format_type = param.validation_rules["format"]
                if format_type in format_examples:
                    return format_examples[format_type]
            
            # Check for patterns or enum
            if param.validation_rules:
                if "enum" in param.validation_rules:
                    return param.validation_rules["enum"][0]
            
            # Generate based on name/description
            name_lower = param.name.lower()
            if "name" in name_lower:
                return "example_name"
            elif "query" in name_lower or "search" in name_lower:
                return "search query"
            elif "path" in name_lower:
                return "/path/to/resource"
            elif "message" in name_lower:
                return "Example message"
            else:
                return "example_value"
        
        elif param.type == ParameterType.INTEGER:
            if param.validation_rules:
                min_val = param.validation_rules.get("minimum", 0)
                max_val = param.validation_rules.get("maximum", 100)
                return min(max(42, min_val), max_val)
            return 42
        
        elif param.type == ParameterType.NUMBER:
            if param.validation_rules:
                min_val = param.validation_rules.get("minimum", 0.0)
                max_val = param.validation_rules.get("maximum", 100.0)
                return min(max(42.5, min_val), max_val)
            return 42.5
        
        elif param.type == ParameterType.BOOLEAN:
            return True
        
        elif param.type == ParameterType.ARRAY:
            return ["item1", "item2"]
        
        elif param.type == ParameterType.OBJECT:
            return {"key": "value"}
        
        else:
            return None
    def _generate_example_output(self, description: ToolDescription) -> Dict[str, Any]:
        """Generate example output based on tool description"""
        category = description.category.lower()
        
        if category == "search":
            return {
                "results": [
                    {"title": "Example Result 1", "url": "https://example.com/1", "snippet": "Example snippet..."},
                    {"title": "Example Result 2", "url": "https://example.com/2", "snippet": "Another snippet..."}
                ],
                "total_count": 2
            }
        elif category == "data":
            return {
                "data": [{"id": 1, "value": "example"}, {"id": 2, "value": "another"}],
                "metadata": {"count": 2, "processed_at": "2024-01-15T10:30:00Z"}
            }
        elif category == "file":
            return {
                "success": True,
                "file_path": "/path/to/file.txt",
                "size": 1024,
                "modified_at": "2024-01-15T10:30:00Z"
            }
        elif category == "api":
            return {
                "status": "success",
                "data": {"result": "operation completed successfully"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        else:
            return {
                "success": True,
                "message": f"{description.name} executed successfully",
                "result": "example result"
            }
