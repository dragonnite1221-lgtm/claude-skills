# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin5:
    def _compare_schemas(self, base_path: str, old_schema: Dict, new_schema: Dict, context: str) -> None:
        """Compare schema definitions."""
        # Type changes
        old_type = old_schema.get('type')
        new_type = new_schema.get('type')
        
        if old_type != new_type and old_type is not None and new_type is not None:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.CRITICAL,
                category="schema",
                path=base_path,
                message=f"Schema type changed from '{old_type}' to '{new_type}' for {context}",
                old_value=old_type,
                new_value=new_type,
                migration_guide=f"Update client code to handle {new_type} instead of {old_type}",
                impact_description="Type change will break client parsing and validation"
            ))
        
        # Property changes for object types
        if old_schema.get('type') == 'object' and new_schema.get('type') == 'object':
            self._compare_object_properties(base_path, old_schema, new_schema, context)
        
        # Array item changes
        if old_schema.get('type') == 'array' and new_schema.get('type') == 'array':
            old_items = old_schema.get('items', {})
            new_items = new_schema.get('items', {})
            if old_items != new_items:
                self._compare_schemas(f"{base_path}/items", old_items, new_items, f"{context} items")
    def _compare_object_properties(self, base_path: str, old_schema: Dict, new_schema: Dict, context: str) -> None:
        """Compare object schema properties."""
        old_props = old_schema.get('properties', {})
        new_props = new_schema.get('properties', {})
        old_required = set(old_schema.get('required', []))
        new_required = set(new_schema.get('required', []))
        
        old_prop_names = set(old_props.keys())
        new_prop_names = set(new_props.keys())
        
        # Removed properties
        removed_props = old_prop_names - new_prop_names
        for prop_name in removed_props:
            severity = ChangeSeverity.CRITICAL if prop_name in old_required else ChangeSeverity.HIGH
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=severity,
                category="schema",
                path=f"{base_path}/properties",
                message=f"Property '{prop_name}' removed from {context}",
                old_value=old_props[prop_name],
                new_value=None,
                migration_guide=f"Remove references to '{prop_name}' property in client code",
                impact_description="Clients expecting this property will receive incomplete data"
            ))
        
        # Added properties
        added_props = new_prop_names - old_prop_names
        for prop_name in added_props:
            if prop_name in new_required:
                # This is handled separately in required field changes
                pass
            else:
                self.report.add_change(Change(
                    change_type=ChangeType.NON_BREAKING,
                    severity=ChangeSeverity.INFO,
                    category="schema",
                    path=f"{base_path}/properties",
                    message=f"New optional property '{prop_name}' added to {context}",
                    old_value=None,
                    new_value=new_props[prop_name],
                    impact_description="New property provides additional data without breaking existing clients"
                ))
        
        # Required field changes
        added_required = new_required - old_required
        removed_required = old_required - new_required
        
        for prop_name in added_required:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.CRITICAL,
                category="schema",
                path=f"{base_path}/properties",
                message=f"Property '{prop_name}' is now required in {context}",
                old_value=False,
                new_value=True,
                migration_guide=f"Ensure '{prop_name}' is always provided when sending {context}",
                impact_description="Clients not providing this property will receive validation errors"
            ))
        
        for prop_name in removed_required:
            self.report.add_change(Change(
                change_type=ChangeType.NON_BREAKING,
                severity=ChangeSeverity.INFO,
                category="schema",
                path=f"{base_path}/properties",
                message=f"Property '{prop_name}' is no longer required in {context}",
                old_value=True,
                new_value=False,
                impact_description="Property is now optional, providing more flexibility"
            ))
        
        # Modified properties
        common_props = old_prop_names & new_prop_names
        for prop_name in common_props:
            old_prop = old_props[prop_name]
            new_prop = new_props[prop_name]
            if old_prop != new_prop:
                self._compare_schemas(f"{base_path}/properties/{prop_name}", 
                                    old_prop, new_prop, f"{context}.{prop_name}")
