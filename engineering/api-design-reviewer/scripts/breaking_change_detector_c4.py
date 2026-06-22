# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin4:
    def _compare_responses(self, base_path: str, old_responses: Dict, new_responses: Dict) -> None:
        """Compare response specifications."""
        responses_path = f"{base_path}/responses"
        
        old_status_codes = set(old_responses.keys())
        new_status_codes = set(new_responses.keys())
        
        # Removed status codes
        removed_codes = old_status_codes - new_status_codes
        for code in removed_codes:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.HIGH,
                category="responses",
                path=f"{responses_path}/{code}",
                message=f"Response status code {code} removed",
                old_value=old_responses[code],
                new_value=None,
                migration_guide=f"Handle alternative status codes: {list(new_status_codes)}",
                impact_description=f"Clients expecting status code {code} need to handle different responses"
            ))
        
        # Added status codes
        added_codes = new_status_codes - old_status_codes
        for code in added_codes:
            self.report.add_change(Change(
                change_type=ChangeType.NON_BREAKING,
                severity=ChangeSeverity.INFO,
                category="responses",
                path=f"{responses_path}/{code}",
                message=f"New response status code {code} added",
                old_value=None,
                new_value=new_responses[code],
                impact_description="New status code provides more specific response information"
            ))
        
        # Modified responses
        common_codes = old_status_codes & new_status_codes
        for code in common_codes:
            self._compare_response_details(responses_path, code, old_responses[code], new_responses[code])
    def _compare_response_details(self, base_path: str, status_code: str, 
                                old_response: Dict, new_response: Dict) -> None:
        """Compare individual response details."""
        response_path = f"{base_path}/{status_code}"
        
        # Compare content types and schemas
        old_content = old_response.get('content', {})
        new_content = new_response.get('content', {})
        
        self._compare_content_types(response_path, old_content, new_content, f"response {status_code}")
    def _compare_content_types(self, base_path: str, old_content: Dict, new_content: Dict, context: str) -> None:
        """Compare content types and their schemas."""
        old_types = set(old_content.keys())
        new_types = set(new_content.keys())
        
        # Removed content types
        removed_types = old_types - new_types
        for content_type in removed_types:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.HIGH,
                category="content_types",
                path=f"{base_path}/content",
                message=f"Content type '{content_type}' removed from {context}",
                old_value=content_type,
                new_value=None,
                migration_guide=f"Use alternative content types: {list(new_types)}",
                impact_description=f"Clients expecting '{content_type}' need to handle different formats"
            ))
        
        # Added content types
        added_types = new_types - old_types
        for content_type in added_types:
            self.report.add_change(Change(
                change_type=ChangeType.ENHANCEMENT,
                severity=ChangeSeverity.INFO,
                category="content_types",
                path=f"{base_path}/content",
                message=f"New content type '{content_type}' added to {context}",
                old_value=None,
                new_value=content_type,
                impact_description=f"Additional format option available for {context}"
            ))
        
        # Modified schemas for common content types
        common_types = old_types & new_types
        for content_type in common_types:
            old_media = old_content[content_type]
            new_media = new_content[content_type]
            
            old_schema = old_media.get('schema', {})
            new_schema = new_media.get('schema', {})
            
            if old_schema != new_schema:
                schema_path = f"{base_path}/content/{content_type}/schema"
                self._compare_schemas(schema_path, old_schema, new_schema, f"{context} ({content_type})")
