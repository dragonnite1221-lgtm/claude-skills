# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compatibility_checker_base import *  # noqa: F403,E402
from compatibility_checker_p0 import CompatibilityIssue, MigrationScript  # noqa: F401,E501


class SchemaCompatibilityCheckerMixin7:
    def _analyze_model_changes(self, model_name: str, before_model: Dict[str, Any], 
                             after_model: Dict[str, Any]) -> Tuple[List[CompatibilityIssue], List[MigrationScript]]:
        """Analyze changes to an API data model"""
        issues = []
        scripts = []
        
        before_props = before_model.get("properties", {})
        after_props = after_model.get("properties", {})
        before_required = set(before_model.get("required", []))
        after_required = set(after_model.get("required", []))
        
        # Check for removed properties
        for prop_name in set(before_props.keys()) - set(after_props.keys()):
            issues.append(CompatibilityIssue(
                type="property_removed",
                severity="breaking",
                description=f"Property '{prop_name}' removed from model '{model_name}'",
                field_path=f"components.schemas.{model_name}.properties.{prop_name}",
                old_value=before_props[prop_name],
                new_value=None,
                impact="Client code expecting this property will fail",
                suggested_migration="Use API versioning to maintain backward compatibility",
                affected_operations=["Serialization", "Deserialization"]
            ))
        
        # Check for newly required properties
        for prop_name in after_required - before_required:
            issues.append(CompatibilityIssue(
                type="property_made_required",
                severity="breaking",
                description=f"Property '{prop_name}' is now required in model '{model_name}'",
                field_path=f"components.schemas.{model_name}.required",
                old_value=list(before_required),
                new_value=list(after_required),
                impact="Client requests without this property will fail validation",
                suggested_migration="Provide default values or implement gradual rollout",
                affected_operations=["Request validation"]
            ))
        
        # Check for property type changes
        for prop_name in set(before_props.keys()) & set(after_props.keys()):
            before_type = before_props[prop_name].get("type")
            after_type = after_props[prop_name].get("type")
            
            if before_type != after_type:
                compatibility = self.type_compatibility_matrix.get(before_type, {}).get(after_type, "breaking")
                issues.append(CompatibilityIssue(
                    type="property_type_changed",
                    severity=compatibility,
                    description=f"Property '{prop_name}' type changed from {before_type} to {after_type} in model '{model_name}'",
                    field_path=f"components.schemas.{model_name}.properties.{prop_name}.type",
                    old_value=before_type,
                    new_value=after_type,
                    impact="Client serialization/deserialization may fail",
                    suggested_migration="Implement type coercion or API versioning",
                    affected_operations=["Serialization", "Deserialization"]
                ))
        
        return issues, scripts
