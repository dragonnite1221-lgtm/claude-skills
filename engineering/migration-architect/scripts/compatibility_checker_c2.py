# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, CompatibilityReport  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin2:
    def analyze_api_schema(self, before_schema: Dict[str, Any], 
                          after_schema: Dict[str, Any]) -> CompatibilityReport:
        """Analyze REST API schema compatibility"""
        issues = []
        migration_scripts = []
        
        # Analyze endpoints
        before_paths = before_schema.get("paths", {})
        after_paths = after_schema.get("paths", {})
        
        # Check for removed endpoints
        for path in before_paths:
            if path not in after_paths:
                for method in before_paths[path]:
                    issues.append(CompatibilityIssue(
                        type="endpoint_removed",
                        severity="breaking",
                        description=f"Endpoint {method.upper()} {path} has been removed",
                        field_path=f"paths.{path}.{method}",
                        old_value=before_paths[path][method],
                        new_value=None,
                        impact="Client requests to this endpoint will fail with 404",
                        suggested_migration=f"Implement redirect to replacement endpoint or maintain backward compatibility stub",
                        affected_operations=[f"{method.upper()} {path}"]
                    ))
        
        # Check for modified endpoints
        for path in set(before_paths.keys()) & set(after_paths.keys()):
            path_issues, path_scripts = self._analyze_endpoint_changes(
                path, before_paths[path], after_paths[path]
            )
            issues.extend(path_issues)
            migration_scripts.extend(path_scripts)
        
        # Analyze data models
        before_components = before_schema.get("components", {}).get("schemas", {})
        after_components = after_schema.get("components", {}).get("schemas", {})
        
        for model_name in set(before_components.keys()) & set(after_components.keys()):
            model_issues, model_scripts = self._analyze_model_changes(
                model_name, before_components[model_name], after_components[model_name]
            )
            issues.extend(model_issues)
            migration_scripts.extend(model_scripts)
        
        return self._build_compatibility_report(
            before_schema, after_schema, issues, migration_scripts
        )
