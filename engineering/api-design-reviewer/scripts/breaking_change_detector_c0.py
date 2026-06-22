# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from breaking_change_detector_base import *  # noqa: F403,E402
from breaking_change_detector_p0 import Change, ChangeSeverity, ChangeType, ComparisonReport  # noqa: F401,E501


class BreakingChangeDetectorMixin0:
    """Main breaking change detection engine."""
    def __init__(self):
        self.report = ComparisonReport()
        self.old_spec: Optional[Dict] = None
        self.new_spec: Optional[Dict] = None
    def compare_specs(self, old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> ComparisonReport:
        """Compare two API specifications and detect changes."""
        self.old_spec = old_spec
        self.new_spec = new_spec
        self.report = ComparisonReport()
        
        # Compare different sections of the API specification
        self._compare_info_section()
        self._compare_servers_section()
        self._compare_paths_section()
        self._compare_components_section()
        self._compare_security_section()
        
        # Calculate summary statistics
        self.report.calculate_summary()
        
        return self.report
    def _compare_info_section(self) -> None:
        """Compare API info sections."""
        old_info = self.old_spec.get('info', {})
        new_info = self.new_spec.get('info', {})
        
        # Version comparison
        old_version = old_info.get('version', '')
        new_version = new_info.get('version', '')
        
        if old_version != new_version:
            self.report.add_change(Change(
                change_type=ChangeType.NON_BREAKING,
                severity=ChangeSeverity.INFO,
                category="versioning",
                path="/info/version",
                message=f"API version changed from '{old_version}' to '{new_version}'",
                old_value=old_version,
                new_value=new_version,
                impact_description="Version change indicates API evolution"
            ))
        
        # Title comparison
        old_title = old_info.get('title', '')
        new_title = new_info.get('title', '')
        
        if old_title != new_title:
            self.report.add_change(Change(
                change_type=ChangeType.NON_BREAKING,
                severity=ChangeSeverity.INFO,
                category="metadata",
                path="/info/title",
                message=f"API title changed from '{old_title}' to '{new_title}'",
                old_value=old_title,
                new_value=new_title,
                impact_description="Title change is cosmetic and doesn't affect functionality"
            ))
    def _compare_servers_section(self) -> None:
        """Compare server configurations."""
        old_servers = self.old_spec.get('servers', [])
        new_servers = self.new_spec.get('servers', [])
        
        old_urls = {server.get('url', '') for server in old_servers if isinstance(server, dict)}
        new_urls = {server.get('url', '') for server in new_servers if isinstance(server, dict)}
        
        # Removed servers
        removed_urls = old_urls - new_urls
        for url in removed_urls:
            self.report.add_change(Change(
                change_type=ChangeType.BREAKING,
                severity=ChangeSeverity.HIGH,
                category="servers",
                path="/servers",
                message=f"Server URL removed: {url}",
                old_value=url,
                new_value=None,
                migration_guide=f"Update client configurations to use alternative server URLs: {list(new_urls)}",
                impact_description="Clients configured to use removed server URL will fail to connect"
            ))
        
        # Added servers
        added_urls = new_urls - old_urls
        for url in added_urls:
            self.report.add_change(Change(
                change_type=ChangeType.ENHANCEMENT,
                severity=ChangeSeverity.INFO,
                category="servers",
                path="/servers",
                message=f"New server URL added: {url}",
                old_value=None,
                new_value=url,
                impact_description="New server option provides additional deployment flexibility"
            ))
