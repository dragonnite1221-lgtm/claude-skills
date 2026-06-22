# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tool_schema_generator_base import *  # noqa: F403,E402
from tool_schema_generator_p0 import ParameterSpec, RateLimitSpec, ToolDescription  # noqa: F401,E501


class ToolSchemaGeneratorMixin5:
    def generate_rate_limits(self, description: ToolDescription) -> RateLimitSpec:
        """Generate rate limiting specification"""
        rate_limits = description.rate_limits
        
        # Default rate limits based on tool category
        defaults = {
            "search": {"rpm": 60, "rph": 1000, "rpd": 10000, "burst": 10},
            "data": {"rpm": 30, "rph": 500, "rpd": 5000, "burst": 5},
            "api": {"rpm": 100, "rph": 2000, "rpd": 20000, "burst": 20},
            "file": {"rpm": 120, "rph": 3000, "rpd": 30000, "burst": 30},
            "compute": {"rpm": 10, "rph": 100, "rpd": 1000, "burst": 3},
            "communication": {"rpm": 30, "rph": 300, "rpd": 3000, "burst": 5}
        }
        
        category_defaults = defaults.get(description.category.lower(), defaults["api"])
        
        return RateLimitSpec(
            requests_per_minute=rate_limits.get("requests_per_minute", category_defaults["rpm"]),
            requests_per_hour=rate_limits.get("requests_per_hour", category_defaults["rph"]),
            requests_per_day=rate_limits.get("requests_per_day", category_defaults["rpd"]),
            burst_limit=rate_limits.get("burst_limit", category_defaults["burst"]),
            cooldown_period=rate_limits.get("cooldown_period", 60),
            rate_limit_key=rate_limits.get("rate_limit_key", "user_id")
        )
    def generate_examples(self, description: ToolDescription, input_params: List[ParameterSpec]) -> List[Dict[str, Any]]:
        """Generate usage examples"""
        examples = []
        
        # Use provided examples if available
        if description.examples:
            for example in description.examples:
                examples.append(example)
        
        # Generate synthetic examples
        if len(examples) == 0:
            synthetic_example = self._generate_synthetic_example(description, input_params)
            if synthetic_example:
                examples.append(synthetic_example)
        
        # Ensure we have multiple examples showing different scenarios
        if len(examples) == 1 and len(input_params) > 1:
            # Generate minimal example
            minimal_example = self._generate_minimal_example(description, input_params)
            if minimal_example and minimal_example != examples[0]:
                examples.append(minimal_example)
        
        return examples
    def _generate_synthetic_example(self, description: ToolDescription, input_params: List[ParameterSpec]) -> Dict[str, Any]:
        """Generate a synthetic example based on parameter specifications"""
        example_input = {}
        
        for param in input_params:
            if param.examples:
                example_input[param.name] = param.examples[0]
            elif param.default is not None:
                example_input[param.name] = param.default
            else:
                example_input[param.name] = self._generate_example_value(param)
        
        # Generate expected output based on tool purpose
        expected_output = self._generate_example_output(description)
        
        return {
            "description": f"Example usage of {description.name}",
            "input": example_input,
            "expected_output": expected_output
        }
    def _generate_minimal_example(self, description: ToolDescription, input_params: List[ParameterSpec]) -> Dict[str, Any]:
        """Generate minimal example with only required parameters"""
        example_input = {}
        
        for param in input_params:
            if param.required:
                if param.examples:
                    example_input[param.name] = param.examples[0]
                else:
                    example_input[param.name] = self._generate_example_value(param)
        
        if not example_input:
            return None
        
        expected_output = self._generate_example_output(description)
        
        return {
            "description": f"Minimal example of {description.name} with required parameters only",
            "input": example_input,
            "expected_output": expected_output
        }
