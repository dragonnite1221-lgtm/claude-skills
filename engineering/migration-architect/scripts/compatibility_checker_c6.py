# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin6:
    def _analyze_endpoint_changes(self, path: str, before_endpoint: Dict[str, Any], 
                                after_endpoint: Dict[str, Any]) -> Tuple[List[CompatibilityIssue], List[MigrationScript]]:
        """Analyze changes to an API endpoint"""
        issues = []
        scripts = []
        
        for method in set(before_endpoint.keys()) & set(after_endpoint.keys()):
            before_method = before_endpoint[method]
            after_method = after_endpoint[method]
            
            # Check parameter changes
            before_params = before_method.get("parameters", [])
            after_params = after_method.get("parameters", [])
            
            before_param_names = {p["name"] for p in before_params}
            after_param_names = {p["name"] for p in after_params}
            
            # Check for removed required parameters
            for param_name in before_param_names - after_param_names:
                param = next(p for p in before_params if p["name"] == param_name)
                if param.get("required", False):
                    issues.append(CompatibilityIssue(
                        type="required_parameter_removed",
                        severity="breaking",
                        description=f"Required parameter '{param_name}' removed from {method.upper()} {path}",
                        field_path=f"paths.{path}.{method}.parameters",
                        old_value=param,
                        new_value=None,
                        impact="Client requests with this parameter will fail",
                        suggested_migration="Implement parameter validation with backward compatibility",
                        affected_operations=[f"{method.upper()} {path}"]
                    ))
            
            # Check for added required parameters
            for param_name in after_param_names - before_param_names:
                param = next(p for p in after_params if p["name"] == param_name)
                if param.get("required", False):
                    issues.append(CompatibilityIssue(
                        type="required_parameter_added",
                        severity="breaking",
                        description=f"New required parameter '{param_name}' added to {method.upper()} {path}",
                        field_path=f"paths.{path}.{method}.parameters",
                        old_value=None,
                        new_value=param,
                        impact="Client requests without this parameter will fail",
                        suggested_migration="Provide default value or make parameter optional initially",
                        affected_operations=[f"{method.upper()} {path}"]
                    ))
            
            # Check response schema changes
            before_responses = before_method.get("responses", {})
            after_responses = after_method.get("responses", {})
            
            for status_code in before_responses:
                if status_code in after_responses:
                    before_schema = before_responses[status_code].get("content", {}).get("application/json", {}).get("schema", {})
                    after_schema = after_responses[status_code].get("content", {}).get("application/json", {}).get("schema", {})
                    
                    if before_schema != after_schema:
                        issues.append(CompatibilityIssue(
                            type="response_schema_changed",
                            severity="potentially_breaking",
                            description=f"Response schema changed for {method.upper()} {path} (status {status_code})",
                            field_path=f"paths.{path}.{method}.responses.{status_code}",
                            old_value=before_schema,
                            new_value=after_schema,
                            impact="Client response parsing may fail",
                            suggested_migration="Implement versioned API responses",
                            affected_operations=[f"{method.upper()} {path}"]
                        ))
        
        return issues, scripts
