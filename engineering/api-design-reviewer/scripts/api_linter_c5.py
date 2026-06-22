# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue  # noqa: F401,E501


class APILinterMixin5:
    def _validate_parameters(self, path: str, method: str, parameters: List[Dict[str, Any]]) -> bool:
        """Validate parameter definitions."""
        has_issues = False
        
        for i, param in enumerate(parameters):
            param_path = f"/paths/{path}/{method.lower()}/parameters[{i}]"
            
            # Check required fields
            if 'name' not in param:
                self.report.add_issue(LintIssue(
                    severity='error',
                    category='parameters',
                    message=f"Parameter missing name field in {method} {path}",
                    path=f"{param_path}/name",
                    suggestion="Add a name field to the parameter"
                ))
                has_issues = True
                continue
            
            if 'in' not in param:
                self.report.add_issue(LintIssue(
                    severity='error',
                    category='parameters',
                    message=f"Parameter '{param['name']}' missing 'in' field in {method} {path}",
                    path=f"{param_path}/in",
                    suggestion="Specify parameter location (query, path, header, cookie)"
                ))
                has_issues = True
            
            # Validate parameter naming
            param_name = param['name']
            param_location = param.get('in', '')
            
            if param_location == 'query':
                # Query parameters should use camelCase or kebab-case
                if not self.camel_case_pattern.match(param_name) and not self.kebab_case_pattern.match(param_name):
                    self.report.add_issue(LintIssue(
                        severity='warning',
                        category='naming',
                        message=f"Query parameter '{param_name}' should use camelCase or kebab-case in {method} {path}",
                        path=f"{param_path}/name",
                        suggestion="Use camelCase (e.g., 'pageSize') or kebab-case (e.g., 'page-size')"
                    ))
                    has_issues = True
            
            elif param_location == 'path':
                # Path parameters should use camelCase or kebab-case
                if not self.camel_case_pattern.match(param_name) and not self.kebab_case_pattern.match(param_name):
                    self.report.add_issue(LintIssue(
                        severity='warning',
                        category='naming',
                        message=f"Path parameter '{param_name}' should use camelCase or kebab-case in {method} {path}",
                        path=f"{param_path}/name",
                        suggestion="Use camelCase (e.g., 'userId') or kebab-case (e.g., 'user-id')"
                    ))
                    has_issues = True
                
                # Path parameters must be required
                if not param.get('required', False):
                    self.report.add_issue(LintIssue(
                        severity='error',
                        category='parameters',
                        message=f"Path parameter '{param_name}' must be required in {method} {path}",
                        path=f"{param_path}/required",
                        suggestion="Set required: true for path parameters"
                    ))
                    has_issues = True
        
        return has_issues
    def _validate_request_body(self, path: str, method: str, request_body: Dict[str, Any]) -> bool:
        """Validate request body definition."""
        has_issues = False
        
        if 'content' not in request_body:
            self.report.add_issue(LintIssue(
                severity='error',
                category='request_body',
                message=f"Request body missing content for {method} {path}",
                path=f"/paths/{path}/{method.lower()}/requestBody/content",
                suggestion="Define content types for the request body"
            ))
            has_issues = True
        
        return has_issues
    def _validate_components_section(self) -> None:
        """Validate the components section."""
        if 'components' not in self.openapi_spec:
            self.report.add_issue(LintIssue(
                severity='info',
                category='structure',
                message="Missing components section",
                path="/components",
                suggestion="Consider defining reusable components (schemas, responses, parameters)"
            ))
            return
        
        components = self.openapi_spec['components']
        
        # Validate schemas
        if 'schemas' in components:
            self._validate_schemas(components['schemas'])
