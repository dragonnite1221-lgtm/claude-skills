# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ToolDescription, ToolSchema  # noqa: F401,E501


class ToolSchemaGeneratorMixin7:
    def generate_tool_schema(self, description: ToolDescription) -> ToolSchema:
        """Generate complete tool schema"""
        # Parse parameters
        input_params, output_params = self.parse_tool_description(description)
        
        # Generate schemas
        openai_schema = self.generate_openai_schema(description, input_params)
        anthropic_schema = self.generate_anthropic_schema(description, input_params)
        
        # Generate validation rules
        validation_rules = []
        for param in input_params:
            if param.validation_rules:
                validation_rules.append({
                    "parameter": param.name,
                    "rules": param.validation_rules
                })
        
        # Generate error responses
        error_responses = self.generate_error_responses(description)
        
        # Generate rate limits
        rate_limits = self.generate_rate_limits(description)
        
        # Generate examples
        examples = self.generate_examples(description, input_params)
        
        # Generate metadata
        metadata = {
            "category": description.category,
            "idempotent": description.idempotent,
            "side_effects": description.side_effects,
            "dependencies": description.dependencies,
            "security_requirements": description.security_requirements,
            "generated_at": "2024-01-15T10:30:00Z",
            "schema_version": "1.0",
            "input_parameters": len(input_params),
            "output_parameters": len(output_params),
            "required_parameters": sum(1 for p in input_params if p.required),
            "optional_parameters": sum(1 for p in input_params if not p.required)
        }
        
        return ToolSchema(
            name=description.name,
            description=description.purpose,
            openai_schema=openai_schema,
            anthropic_schema=anthropic_schema,
            validation_rules=validation_rules,
            error_responses=error_responses,
            rate_limits=rate_limits,
            examples=examples,
            metadata=metadata
        )
