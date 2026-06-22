# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue  # noqa: F401,E501


class APILinterMixin3:
    def _validate_operation(self, path: str, method: str, operation: Dict[str, Any]) -> bool:
        """Validate individual operation (HTTP method + path combination)."""
        has_issues = False
        operation_path = f"/paths/{path}/{method.lower()}"
        
        # Check for required operation fields
        if 'responses' not in operation:
            self.report.add_issue(LintIssue(
                severity='error',
                category='structure',
                message=f"Missing responses section for {method} {path}",
                path=f"{operation_path}/responses",
                suggestion="Define expected responses for this operation"
            ))
            has_issues = True
        
        # Check for operation documentation
        if 'summary' not in operation:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='documentation',
                message=f"Missing summary for {method} {path}",
                path=f"{operation_path}/summary",
                suggestion="Add a brief summary describing what this operation does"
            ))
            has_issues = True
        
        if 'description' not in operation:
            self.report.add_issue(LintIssue(
                severity='info',
                category='documentation',
                message=f"Missing description for {method} {path}",
                path=f"{operation_path}/description",
                suggestion="Add a detailed description for better API documentation"
            ))
            has_issues = True
        
        # Validate HTTP method usage patterns
        method_issues = self._validate_http_method_usage(path, method, operation)
        if method_issues:
            has_issues = True
        
        # Validate responses
        if 'responses' in operation:
            response_issues = self._validate_responses(path, method, operation['responses'])
            if response_issues:
                has_issues = True
        
        # Validate parameters
        if 'parameters' in operation:
            param_issues = self._validate_parameters(path, method, operation['parameters'])
            if param_issues:
                has_issues = True
        
        # Validate request body
        if 'requestBody' in operation:
            body_issues = self._validate_request_body(path, method, operation['requestBody'])
            if body_issues:
                has_issues = True
        
        return has_issues
    def _validate_http_method_usage(self, path: str, method: str, operation: Dict[str, Any]) -> bool:
        """Validate proper HTTP method usage patterns."""
        has_issues = False
        
        # GET requests should not have request body
        if method == 'GET' and 'requestBody' in operation:
            self.report.add_issue(LintIssue(
                severity='error',
                category='rest_conventions',
                message=f"GET request should not have request body: {method} {path}",
                path=f"/paths/{path}/{method.lower()}/requestBody",
                suggestion="Remove requestBody from GET request or use POST if body is needed"
            ))
            has_issues = True
        
        # DELETE requests typically should not have request body
        if method == 'DELETE' and 'requestBody' in operation:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='rest_conventions',
                message=f"DELETE request typically should not have request body: {method} {path}",
                path=f"/paths/{path}/{method.lower()}/requestBody",
                suggestion="Consider using query parameters or path parameters instead"
            ))
            has_issues = True
        
        # POST/PUT/PATCH should typically have request body (except for actions)
        if method in ['POST', 'PUT', 'PATCH'] and 'requestBody' not in operation:
            # Check if this is an action endpoint
            if not any(action in path.lower() for action in ['activate', 'deactivate', 'reset', 'confirm']):
                self.report.add_issue(LintIssue(
                    severity='info',
                    category='rest_conventions',
                    message=f"{method} request typically should have request body: {method} {path}",
                    path=f"/paths/{path}/{method.lower()}",
                    suggestion=f"Consider adding requestBody for {method} operation or use GET if no data is being sent"
                ))
                has_issues = True
        
        return has_issues
