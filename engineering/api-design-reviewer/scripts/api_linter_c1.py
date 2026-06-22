# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue  # noqa: F401,E501


class APILinterMixin1:
    def _validate_info_section(self) -> None:
        """Validate the info section of OpenAPI spec."""
        if 'info' not in self.openapi_spec:
            return
            
        info = self.openapi_spec['info']
        required_info_fields = ['title', 'version']
        recommended_info_fields = ['description', 'contact']
        
        for field in required_info_fields:
            if field not in info:
                self.report.add_issue(LintIssue(
                    severity='error',
                    category='documentation',
                    message=f"Missing required info field: {field}",
                    path=f"/info/{field}",
                    suggestion=f"Add a '{field}' field to the info section"
                ))
        
        for field in recommended_info_fields:
            if field not in info:
                self.report.add_issue(LintIssue(
                    severity='warning',
                    category='documentation',
                    message=f"Missing recommended info field: {field}",
                    path=f"/info/{field}",
                    suggestion=f"Consider adding a '{field}' field to improve API documentation"
                ))
        
        # Validate version format
        if 'version' in info:
            version = info['version']
            if not re.match(r'^\d+\.\d+(\.\d+)?(-\w+)?$', version):
                self.report.add_issue(LintIssue(
                    severity='warning',
                    category='versioning',
                    message=f"Version format '{version}' doesn't follow semantic versioning",
                    path="/info/version",
                    suggestion="Use semantic versioning format (e.g., '1.0.0', '2.1.3-beta')"
                ))
    def _validate_servers_section(self) -> None:
        """Validate the servers section."""
        if 'servers' not in self.openapi_spec:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='configuration',
                message="Missing servers section",
                path="/servers",
                suggestion="Add a servers section to specify API base URLs"
            ))
            return
        
        servers = self.openapi_spec['servers']
        if not isinstance(servers, list) or len(servers) == 0:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='configuration',
                message="Empty servers section",
                path="/servers",
                suggestion="Add at least one server URL"
            ))
    def _validate_paths_section(self) -> None:
        """Validate all API paths and operations."""
        if 'paths' not in self.openapi_spec:
            return
            
        paths = self.openapi_spec['paths']
        if not paths:
            self.report.add_issue(LintIssue(
                severity='error',
                category='structure',
                message="No paths defined in API specification",
                path="/paths",
                suggestion="Define at least one API endpoint"
            ))
            return
        
        self.report.total_endpoints = sum(
            len([method for method in path_obj.keys() if method.upper() in self.http_methods])
            for path_obj in paths.values() if isinstance(path_obj, dict)
        )
        
        endpoints_with_issues = set()
        
        for path, path_obj in paths.items():
            if not isinstance(path_obj, dict):
                continue
                
            # Validate path structure
            path_issues = self._validate_path_structure(path)
            if path_issues:
                endpoints_with_issues.add(path)
            
            # Validate each operation in the path
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                    
                operation_issues = self._validate_operation(path, method.upper(), operation)
                if operation_issues:
                    endpoints_with_issues.add(path)
        
        self.report.endpoints_with_issues = len(endpoints_with_issues)
