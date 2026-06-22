# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType  # noqa: F401,E501


class BreakingChangeDetectorMixin3:
    def _compare_request_body(self, base_path: str, old_body: Optional[Dict], new_body: Optional[Dict]) -> None:
        """Compare request body specifications."""
        body_path = f"{base_path}/requestBody"
        
        # Request body added
        if old_body is None and new_body is not None:
            is_required = new_body.get('required', False)
            if is_required:
                self.report.add_change(Change(
                    change_type=ChangeType.BREAKING,
                    severity=ChangeSeverity.HIGH,
                    category="request_body",
                    path=body_path,
                    message="Required request body added",
                    old_value=None,
                    new_value=new_body,
                    migration_guide="Include request body with appropriate content type when calling this endpoint",
                    impact_description="Clients not providing request body will receive validation errors"
                ))
            else:
                self.report.add_change(Change(
                    change_type=ChangeType.NON_BREAKING,
                    severity=ChangeSeverity.INFO,
                    category="request_body",
                    path=body_path,
                    message="Optional request body added",
                    old_value=None,
                    new_value=new_body,
                    impact_description="Optional request body provides additional functionality"
                ))
        
        # Request body removed
        elif old_body is not None and new_body is None:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.HIGH,
                category="request_body",
                path=body_path,
                message="Request body removed",
                old_value=old_body,
                new_value=None,
                migration_guide="Remove request body when calling this endpoint",
                impact_description="Clients sending request body may receive validation errors"
            ))
        
        # Request body modified
        elif old_body is not None and new_body is not None:
            self._compare_request_body_details(body_path, old_body, new_body)
    def _compare_request_body_details(self, base_path: str, old_body: Dict, new_body: Dict) -> None:
        """Compare request body details."""
        # Required status change
        old_required = old_body.get('required', False)
        new_required = new_body.get('required', False)
        
        if old_required != new_required:
            if new_required:
                self.report.add_change(Change(
                    change_type=ChangeType.BREAKING,
                    severity=ChangeSeverity.HIGH,
                    category="request_body",
                    path=base_path,
                    message="Request body is now required (was optional)",
                    old_value=old_required,
                    new_value=new_required,
                    migration_guide="Always include request body when calling this endpoint",
                    impact_description="Clients not providing request body will receive validation errors"
                ))
            else:
                self.report.add_change(Change(
                    change_type=ChangeType.NON_BREAKING,
                    severity=ChangeSeverity.INFO,
                    category="request_body",
                    path=base_path,
                    message="Request body is now optional (was required)",
                    old_value=old_required,
                    new_value=new_required,
                    impact_description="Request body is now optional, providing more flexibility"
                ))
        
        # Content type changes
        old_content = old_body.get('content', {})
        new_content = new_body.get('content', {})
        self._compare_content_types(base_path, old_content, new_content, "request body")
