# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue, LintReport  # noqa: F401,E501


class APILinterMixin0:
    """Main API linting engine."""
    def __init__(self):
        self.report = LintReport()
        self.openapi_spec: Optional[Dict] = None
        self.raw_endpoints: Optional[Dict] = None
        
        # Regex patterns for naming conventions
        self.kebab_case_pattern = re.compile(r'^[a-z]+(?:-[a-z0-9]+)*$')
        self.camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
        self.snake_case_pattern = re.compile(r'^[a-z]+(?:_[a-z0-9]+)*$')
        self.pascal_case_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
        
        # Standard HTTP methods
        self.http_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'}
        
        # Standard HTTP status codes by method
        self.standard_status_codes = {
            'GET': {200, 304, 404},
            'POST': {200, 201, 400, 409, 422},
            'PUT': {200, 204, 400, 404, 409},
            'PATCH': {200, 204, 400, 404, 409},
            'DELETE': {200, 204, 404},
            'HEAD': {200, 404},
            'OPTIONS': {200}
        }
        
        # Common error status codes
        self.common_error_codes = {400, 401, 403, 404, 405, 409, 422, 429, 500, 502, 503}
    def lint_openapi_spec(self, spec: Dict[str, Any]) -> LintReport:
        """Lint an OpenAPI/Swagger specification."""
        self.openapi_spec = spec
        self.report = LintReport()
        
        # Basic structure validation
        self._validate_openapi_structure()
        
        # Info section validation
        self._validate_info_section()
        
        # Server section validation
        self._validate_servers_section()
        
        # Paths validation (main linting logic)
        self._validate_paths_section()
        
        # Components validation
        self._validate_components_section()
        
        # Security validation
        self._validate_security_section()
        
        # Calculate final score
        self.report.calculate_score()
        
        return self.report
    def lint_raw_endpoints(self, endpoints: Dict[str, Any]) -> LintReport:
        """Lint raw endpoint definitions."""
        self.raw_endpoints = endpoints
        self.report = LintReport()
        
        # Validate raw endpoint structure
        self._validate_raw_endpoint_structure()
        
        # Lint each endpoint
        for endpoint_path, endpoint_data in endpoints.get('endpoints', {}).items():
            self._lint_raw_endpoint(endpoint_path, endpoint_data)
        
        self.report.calculate_score()
        return self.report
    def _validate_openapi_structure(self) -> None:
        """Validate basic OpenAPI document structure."""
        required_fields = ['openapi', 'info', 'paths']
        
        for field in required_fields:
            if field not in self.openapi_spec:
                self.report.add_issue(LintIssue(
                    severity='error',
                    category='structure',
                    message=f"Missing required field: {field}",
                    path=f"/{field}",
                    suggestion=f"Add the '{field}' field to the root of your OpenAPI specification"
                ))
