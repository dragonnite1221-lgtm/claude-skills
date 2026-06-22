# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue  # noqa: F401,E501


class APILinterMixin6:
    def _validate_schemas(self, schemas: Dict[str, Any]) -> None:
        """Validate schema definitions."""
        for schema_name, schema in schemas.items():
            # Check schema naming (should be PascalCase)
            if not self.pascal_case_pattern.match(schema_name):
                self.report.add_issue(LintIssue(
                    severity='warning',
                    category='naming',
                    message=f"Schema name '{schema_name}' should use PascalCase",
                    path=f"/components/schemas/{schema_name}",
                    suggestion=f"Use PascalCase for schema names (e.g., 'UserProfile', 'OrderItem')"
                ))
            
            # Validate schema properties
            if isinstance(schema, dict) and 'properties' in schema:
                self._validate_schema_properties(schema_name, schema['properties'])
    def _validate_schema_properties(self, schema_name: str, properties: Dict[str, Any]) -> None:
        """Validate schema property naming."""
        for prop_name, prop_def in properties.items():
            # Properties should use camelCase
            if not self.camel_case_pattern.match(prop_name):
                self.report.add_issue(LintIssue(
                    severity='warning',
                    category='naming',
                    message=f"Property '{prop_name}' in schema '{schema_name}' should use camelCase",
                    path=f"/components/schemas/{schema_name}/properties/{prop_name}",
                    suggestion="Use camelCase for property names (e.g., 'firstName', 'createdAt')"
                ))
    def _validate_security_section(self) -> None:
        """Validate security definitions."""
        if 'security' not in self.openapi_spec and 'components' not in self.openapi_spec:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='security',
                message="No security configuration found",
                path="/security",
                suggestion="Define security schemes and apply them to operations"
            ))
    def _validate_raw_endpoint_structure(self) -> None:
        """Validate structure of raw endpoint definitions."""
        if 'endpoints' not in self.raw_endpoints:
            self.report.add_issue(LintIssue(
                severity='error',
                category='structure',
                message="Missing 'endpoints' field in raw endpoint definition",
                path="/endpoints",
                suggestion="Provide an 'endpoints' object containing endpoint definitions"
            ))
            return
        
        endpoints = self.raw_endpoints['endpoints']
        self.report.total_endpoints = len(endpoints)
    def _lint_raw_endpoint(self, path: str, endpoint_data: Dict[str, Any]) -> None:
        """Lint individual raw endpoint definition."""
        # Validate path structure
        self._validate_path_structure(path)
        
        # Check for required fields
        if 'method' not in endpoint_data:
            self.report.add_issue(LintIssue(
                severity='error',
                category='structure',
                message=f"Missing method field for endpoint {path}",
                path=f"/endpoints/{path}/method",
                suggestion="Specify HTTP method (GET, POST, PUT, PATCH, DELETE)"
            ))
            return
        
        method = endpoint_data['method'].upper()
        if method not in self.http_methods:
            self.report.add_issue(LintIssue(
                severity='error',
                category='structure',
                message=f"Invalid HTTP method '{method}' for endpoint {path}",
                path=f"/endpoints/{path}/method",
                suggestion=f"Use valid HTTP methods: {', '.join(sorted(self.http_methods))}"
            ))
    def generate_json_report(self) -> str:
        """Generate JSON format report."""
        issues_by_severity = self.report.get_issues_by_severity()
        
        report_data = {
            "summary": {
                "total_endpoints": self.report.total_endpoints,
                "endpoints_with_issues": self.report.endpoints_with_issues,
                "total_issues": len(self.report.issues),
                "errors": len(issues_by_severity['error']),
                "warnings": len(issues_by_severity['warning']),
                "info": len(issues_by_severity['info']),
                "score": round(self.report.score, 2)
            },
            "issues": []
        }
        
        for issue in self.report.issues:
            report_data["issues"].append({
                "severity": issue.severity,
                "category": issue.category,
                "message": issue.message,
                "path": issue.path,
                "suggestion": issue.suggestion
            })
        
        return json.dumps(report_data, indent=2)
