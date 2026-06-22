# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402
from api_linter_p0 import LintIssue  # noqa: F401,E501


class APILinterMixin2:
    def _validate_path_structure(self, path: str) -> bool:
        """Validate REST path structure and naming conventions."""
        has_issues = False
        
        # Check if path starts with slash
        if not path.startswith('/'):
            self.report.add_issue(LintIssue(
                severity='error',
                category='url_structure',
                message=f"Path must start with '/' character: {path}",
                path=f"/paths/{path}",
                suggestion=f"Change '{path}' to '/{path.lstrip('/')}'"
            ))
            has_issues = True
        
        # Split path into segments
        segments = [seg for seg in path.split('/') if seg]
        
        # Check for empty segments (double slashes)
        if '//' in path:
            self.report.add_issue(LintIssue(
                severity='error',
                category='url_structure',
                message=f"Path contains empty segments: {path}",
                path=f"/paths/{path}",
                suggestion="Remove double slashes from the path"
            ))
            has_issues = True
        
        # Validate each segment
        for i, segment in enumerate(segments):
            # Skip parameter segments
            if segment.startswith('{') and segment.endswith('}'):
                # Validate parameter naming
                param_name = segment[1:-1]
                if not self.camel_case_pattern.match(param_name) and not self.kebab_case_pattern.match(param_name):
                    self.report.add_issue(LintIssue(
                        severity='warning',
                        category='naming',
                        message=f"Path parameter '{param_name}' should use camelCase or kebab-case",
                        path=f"/paths/{path}",
                        suggestion=f"Use camelCase (e.g., 'userId') or kebab-case (e.g., 'user-id')"
                    ))
                    has_issues = True
                continue
            
            # Check for resource naming conventions
            if not self.kebab_case_pattern.match(segment):
                # Allow version segments like 'v1', 'v2'
                if not re.match(r'^v\d+$', segment):
                    self.report.add_issue(LintIssue(
                        severity='warning',
                        category='naming',
                        message=f"Resource segment '{segment}' should use kebab-case",
                        path=f"/paths/{path}",
                        suggestion=f"Use kebab-case for '{segment}' (e.g., 'user-profiles', 'order-items')"
                    ))
                    has_issues = True
            
            # Check for verb usage in URLs (anti-pattern)
            common_verbs = {'get', 'post', 'put', 'delete', 'create', 'update', 'remove', 'add'}
            if segment.lower() in common_verbs:
                self.report.add_issue(LintIssue(
                    severity='warning',
                    category='rest_conventions',
                    message=f"Avoid verbs in URLs: '{segment}' in {path}",
                    path=f"/paths/{path}",
                    suggestion="Use HTTP methods instead of verbs in URLs. Use nouns for resources."
                ))
                has_issues = True
        
        # Check path depth (avoid over-nesting)
        if len(segments) > 6:
            self.report.add_issue(LintIssue(
                severity='warning',
                category='url_structure',
                message=f"Path has excessive nesting ({len(segments)} levels): {path}",
                path=f"/paths/{path}",
                suggestion="Consider flattening the resource hierarchy or using query parameters"
            ))
            has_issues = True
        
        # Check for consistent versioning
        if any('v' + str(i) in segments for i in range(1, 10)):
            version_segments = [seg for seg in segments if re.match(r'^v\d+$', seg)]
            if len(version_segments) > 1:
                self.report.add_issue(LintIssue(
                    severity='error',
                    category='versioning',
                    message=f"Multiple version segments in path: {path}",
                    path=f"/paths/{path}",
                    suggestion="Use only one version segment per path"
                ))
                has_issues = True
        
        return has_issues
