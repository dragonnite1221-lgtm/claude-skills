# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue  # noqa: F401,E501


class APILinterMixin4:
    def _validate_responses(self, path: str, method: str, responses: Dict[str, Any]) -> bool:
        """Validate response definitions."""
        has_issues = False
        
        # Check for success response
        success_codes = {'200', '201', '202', '204'}
        has_success = any(code in responses for code in success_codes)
        
        if not has_success:
            self.report.add_issue(LintIssue(
                severity='error',
                category='responses',
                message=f"Missing success response for {method} {path}",
                path=f"/paths/{path}/{method.lower()}/responses",
                suggestion="Define at least one success response (200, 201, 202, or 204)"
            ))
            has_issues = True
        
        # Check for error responses
        has_error_responses = any(code.startswith('4') or code.startswith('5') for code in responses.keys())
        
        if not has_error_responses:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='responses',
                message=f"Missing error responses for {method} {path}",
                path=f"/paths/{path}/{method.lower()}/responses",
                suggestion="Define common error responses (400, 404, 500, etc.)"
            ))
            has_issues = True
        
        # Validate individual response codes
        for status_code, response in responses.items():
            if status_code == 'default':
                continue
                
            try:
                code_int = int(status_code)
            except ValueError:
                self.report.add_issue(LintIssue(
                    severity='error',
                    category='responses',
                    message=f"Invalid status code '{status_code}' for {method} {path}",
                    path=f"/paths/{path}/{method.lower()}/responses/{status_code}",
                    suggestion="Use valid HTTP status codes (e.g., 200, 404, 500)"
                ))
                has_issues = True
                continue
            
            # Check if status code is appropriate for the method
            expected_codes = self.standard_status_codes.get(method, set())
            common_codes = {400, 401, 403, 404, 429, 500}  # Always acceptable
            
            if expected_codes and code_int not in expected_codes and code_int not in common_codes:
                self.report.add_issue(LintIssue(
                    severity='info',
                    category='responses',
                    message=f"Uncommon status code {status_code} for {method} {path}",
                    path=f"/paths/{path}/{method.lower()}/responses/{status_code}",
                    suggestion=f"Consider using standard codes for {method}: {sorted(expected_codes)}"
                ))
                has_issues = True
        
        return has_issues
