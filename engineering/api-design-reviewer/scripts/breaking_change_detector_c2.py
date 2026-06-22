# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin2:
    def _compare_parameters(self, base_path: str, old_params: List[Dict], new_params: List[Dict]) -> None:
        """Compare operation parameters."""
        # Create lookup dictionaries
        old_param_map = {(p.get('name'), p.get('in')): p for p in old_params}
        new_param_map = {(p.get('name'), p.get('in')): p for p in new_params}
        
        old_param_keys = set(old_param_map.keys())
        new_param_keys = set(new_param_map.keys())
        
        # Removed parameters
        removed_params = old_param_keys - new_param_keys
        for param_key in removed_params:
            name, location = param_key
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.HIGH,
                category="parameters",
                path=f"{base_path}/parameters",
                message=f"Parameter removed: {name} (in: {location})",
                old_value=old_param_map[param_key],
                new_value=None,
                migration_guide=f"Remove '{name}' parameter from {location} when calling this endpoint",
                impact_description="Clients sending this parameter may receive validation errors"
            ))
        
        # Added parameters
        added_params = new_param_keys - old_param_keys
        for param_key in added_params:
            name, location = param_key
            new_param = new_param_map[param_key]
            is_required = new_param.get('required', False)
            
            if is_required:
                self.report.add_change(Change(
                    change_type=ChangeType.BREAKING,
                    severity=ChangeSeverity.CRITICAL,
                    category="parameters",
                    path=f"{base_path}/parameters",
                    message=f"New required parameter added: {name} (in: {location})",
                    old_value=None,
                    new_value=new_param,
                    migration_guide=f"Add required '{name}' parameter to {location} when calling this endpoint",
                    impact_description="Clients not providing this parameter will receive 400 Bad Request errors"
                ))
            else:
                self.report.add_change(Change(
                    change_type=ChangeType.NON_BREAKING,
                    severity=ChangeSeverity.INFO,
                    category="parameters",
                    path=f"{base_path}/parameters",
                    message=f"New optional parameter added: {name} (in: {location})",
                    old_value=None,
                    new_value=new_param,
                    impact_description="Optional parameter provides additional functionality"
                ))
        
        # Modified parameters
        common_params = old_param_keys & new_param_keys
        for param_key in common_params:
            name, location = param_key
            old_param = old_param_map[param_key]
            new_param = new_param_map[param_key]
            self._compare_parameter_details(base_path, name, location, old_param, new_param)
    def _compare_parameter_details(self, base_path: str, name: str, location: str, 
                                 old_param: Dict, new_param: Dict) -> None:
        """Compare individual parameter details."""
        param_path = f"{base_path}/parameters/{name}"
        
        # Required status change
        old_required = old_param.get('required', False)
        new_required = new_param.get('required', False)
        
        if old_required != new_required:
            if new_required:
                self.report.add_change(Change(
                    change_type=ChangeType.BREAKING,
                    severity=ChangeSeverity.HIGH,
                    category="parameters",
                    path=param_path,
                    message=f"Parameter '{name}' is now required (was optional)",
                    old_value=old_required,
                    new_value=new_required,
                    migration_guide=f"Ensure '{name}' parameter is always provided when calling this endpoint",
                    impact_description="Clients not providing this parameter will receive validation errors"
                ))
            else:
                self.report.add_change(Change(
                    change_type=ChangeType.NON_BREAKING,
                    severity=ChangeSeverity.INFO,
                    category="parameters",
                    path=param_path,
                    message=f"Parameter '{name}' is now optional (was required)",
                    old_value=old_required,
                    new_value=new_required,
                    impact_description="Parameter is now optional, providing more flexibility to clients"
                ))
        
        # Schema/type changes
        old_schema = old_param.get('schema', {})
        new_schema = new_param.get('schema', {})
        
        if old_schema != new_schema:
            self._compare_schemas(param_path, old_schema, new_schema, f"parameter '{name}'")
