# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin1:
    def _compare_paths_section(self) -> None:
        """Compare API paths and operations."""
        old_paths = self.old_spec.get('paths', {})
        new_paths = self.new_spec.get('paths', {})
        
        # Find removed, added, and modified paths
        old_path_set = set(old_paths.keys())
        new_path_set = set(new_paths.keys())
        
        removed_paths = old_path_set - new_path_set
        added_paths = new_path_set - old_path_set
        common_paths = old_path_set & new_path_set
        
        # Handle removed paths
        for path in removed_paths:
            old_operations = self._extract_operations(old_paths[path])
            for method in old_operations:
                self.report.add_change(Change(
                    change_type=ChangeType.BREAKING,
                    severity=ChangeSeverity.CRITICAL,
                    category="endpoints",
                    path=f"/paths{path}",
                    message=f"Endpoint removed: {method.upper()} {path}",
                    old_value=f"{method.upper()} {path}",
                    new_value=None,
                    migration_guide=self._generate_endpoint_removal_migration(path, method, new_paths),
                    impact_description="Clients using this endpoint will receive 404 errors"
                ))
        
        # Handle added paths
        for path in added_paths:
            new_operations = self._extract_operations(new_paths[path])
            for method in new_operations:
                self.report.add_change(Change(
                    change_type=ChangeType.ENHANCEMENT,
                    severity=ChangeSeverity.INFO,
                    category="endpoints",
                    path=f"/paths{path}",
                    message=f"New endpoint added: {method.upper()} {path}",
                    old_value=None,
                    new_value=f"{method.upper()} {path}",
                    impact_description="New functionality available to clients"
                ))
        
        # Handle modified paths
        for path in common_paths:
            self._compare_path_operations(path, old_paths[path], new_paths[path])
    def _extract_operations(self, path_object: Dict[str, Any]) -> List[str]:
        """Extract HTTP operations from a path object."""
        http_methods = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}
        return [method for method in path_object.keys() if method.lower() in http_methods]
    def _compare_path_operations(self, path: str, old_path_obj: Dict, new_path_obj: Dict) -> None:
        """Compare operations within a specific path."""
        old_operations = set(self._extract_operations(old_path_obj))
        new_operations = set(self._extract_operations(new_path_obj))
        
        # Removed operations
        removed_ops = old_operations - new_operations
        for method in removed_ops:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.CRITICAL,
                category="endpoints",
                path=f"/paths{path}/{method}",
                message=f"HTTP method removed: {method.upper()} {path}",
                old_value=f"{method.upper()} {path}",
                new_value=None,
                migration_guide=self._generate_method_removal_migration(path, method, new_operations),
                impact_description="Clients using this method will receive 405 Method Not Allowed errors"
            ))
        
        # Added operations
        added_ops = new_operations - old_operations
        for method in added_ops:
            self.report.add_change(Change(
                change_type=ChangeType.ENHANCEMENT,
                severity=ChangeSeverity.INFO,
                category="endpoints",
                path=f"/paths{path}/{method}",
                message=f"New HTTP method added: {method.upper()} {path}",
                old_value=None,
                new_value=f"{method.upper()} {path}",
                impact_description="New method provides additional functionality for this resource"
            ))
        
        # Modified operations
        common_ops = old_operations & new_operations
        for method in common_ops:
            self._compare_operation_details(path, method, old_path_obj[method], new_path_obj[method])
    def _compare_operation_details(self, path: str, method: str, old_op: Dict, new_op: Dict) -> None:
        """Compare details of individual operations."""
        operation_path = f"/paths{path}/{method}"
        
        # Compare parameters
        self._compare_parameters(operation_path, old_op.get('parameters', []), new_op.get('parameters', []))
        
        # Compare request body
        self._compare_request_body(operation_path, old_op.get('requestBody'), new_op.get('requestBody'))
        
        # Compare responses
        self._compare_responses(operation_path, old_op.get('responses', {}), new_op.get('responses', {}))
        
        # Compare security requirements
        self._compare_security_requirements(operation_path, old_op.get('security'), new_op.get('security'))
