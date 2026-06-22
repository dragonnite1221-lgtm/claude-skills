# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402


class BreakingChangeDetectorMixin7:
    def _generate_endpoint_removal_migration(self, removed_path: str, method: str, 
                                           remaining_paths: Dict[str, Any]) -> str:
        """Generate migration guide for removed endpoints."""
        # Look for similar endpoints
        similar_paths = []
        path_segments = removed_path.strip('/').split('/')
        
        for existing_path in remaining_paths.keys():
            existing_segments = existing_path.strip('/').split('/')
            if len(existing_segments) == len(path_segments):
                # Check similarity
                similarity = sum(1 for i, seg in enumerate(path_segments) 
                               if i < len(existing_segments) and seg == existing_segments[i])
                if similarity >= len(path_segments) * 0.5:  # At least 50% similar
                    similar_paths.append(existing_path)
        
        if similar_paths:
            return f"Consider using alternative endpoints: {', '.join(similar_paths[:3])}"
        else:
            return "No direct replacement available. Review API documentation for alternative approaches."
    def _generate_method_removal_migration(self, path: str, removed_method: str, 
                                         remaining_methods: Set[str]) -> str:
        """Generate migration guide for removed HTTP methods."""
        method_alternatives = {
            'get': ['head'],
            'post': ['put', 'patch'],
            'put': ['post', 'patch'],
            'patch': ['put', 'post'],
            'delete': []
        }
        
        alternatives = []
        for alt_method in method_alternatives.get(removed_method.lower(), []):
            if alt_method in remaining_methods:
                alternatives.append(alt_method.upper())
        
        if alternatives:
            return f"Use alternative methods: {', '.join(alternatives)}"
        else:
            return f"No alternative HTTP methods available for {path}"
    def generate_json_report(self) -> str:
        """Generate JSON format report."""
        report_data = {
            "summary": self.report.summary,
            "hasBreakingChanges": self.report.has_breaking_changes(),
            "changes": [change.to_dict() for change in self.report.changes]
        }
        
        return json.dumps(report_data, indent=2)
