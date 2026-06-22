# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin6:
    def _compare_security_requirements(self, base_path: str, old_security: Optional[List], 
                                     new_security: Optional[List]) -> None:
        """Compare security requirements."""
        # Simplified security comparison - could be expanded
        if old_security != new_security:
            severity = ChangeSeverity.HIGH if new_security else ChangeSeverity.CRITICAL
            change_type = ChangeType.BREAKING
            
            if old_security is None and new_security is not None:
                message = "Security requirements added"
                migration_guide = "Ensure proper authentication/authorization when calling this endpoint"
                impact = "Endpoint now requires authentication"
            elif old_security is not None and new_security is None:
                message = "Security requirements removed"
                migration_guide = "Authentication is no longer required for this endpoint"
                impact = "Endpoint is now publicly accessible"
                severity = ChangeSeverity.MEDIUM  # Less severe, more permissive
            else:
                message = "Security requirements modified"
                migration_guide = "Update authentication/authorization method for this endpoint"
                impact = "Different authentication method required"
            
            self.report.add_change(Change(
                change_type=change_type,
                severity=severity,
                category="security",
                path=f"{base_path}/security",
                message=message,
                old_value=old_security,
                new_value=new_security,
                migration_guide=migration_guide,
                impact_description=impact
            ))
    def _compare_components_section(self) -> None:
        """Compare components sections."""
        old_components = self.old_spec.get('components', {})
        new_components = self.new_spec.get('components', {})
        
        # Compare schemas
        old_schemas = old_components.get('schemas', {})
        new_schemas = new_components.get('schemas', {})
        
        old_schema_names = set(old_schemas.keys())
        new_schema_names = set(new_schemas.keys())
        
        # Removed schemas
        removed_schemas = old_schema_names - new_schema_names
        for schema_name in removed_schemas:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.HIGH,
                category="components",
                path=f"/components/schemas/{schema_name}",
                message=f"Schema '{schema_name}' removed from components",
                old_value=old_schemas[schema_name],
                new_value=None,
                migration_guide=f"Remove references to schema '{schema_name}' or use alternative schemas",
                impact_description="References to this schema will fail validation"
            ))
        
        # Added schemas
        added_schemas = new_schema_names - old_schema_names
        for schema_name in added_schemas:
            self.report.add_change(Change(
                change_type=ChangeType.ENHANCEMENT,
                severity=ChangeSeverity.INFO,
                category="components",
                path=f"/components/schemas/{schema_name}",
                message=f"New schema '{schema_name}' added to components",
                old_value=None,
                new_value=new_schemas[schema_name],
                impact_description="New reusable schema available"
            ))
        
        # Modified schemas
        common_schemas = old_schema_names & new_schema_names
        for schema_name in common_schemas:
            old_schema = old_schemas[schema_name]
            new_schema = new_schemas[schema_name]
            if old_schema != new_schema:
                self._compare_schemas(f"/components/schemas/{schema_name}", 
                                    old_schema, new_schema, f"schema '{schema_name}'")
    def _compare_security_section(self) -> None:
        """Compare security definitions."""
        old_security_schemes = self.old_spec.get('components', {}).get('securitySchemes', {})
        new_security_schemes = self.new_spec.get('components', {}).get('securitySchemes', {})
        
        if old_security_schemes != new_security_schemes:
            # Simplified comparison - could be more detailed
            self.report.add_change(Change(
                change_type=ChangeType.POTENTIALLY_BREAKING,
                severity=ChangeSeverity.MEDIUM,
                category="security",
                path="/components/securitySchemes",
                message="Security scheme definitions changed",
                old_value=old_security_schemes,
                new_value=new_security_schemes,
                migration_guide="Review authentication implementation for compatibility with new security schemes",
                impact_description="Authentication mechanisms may have changed"
            ))
