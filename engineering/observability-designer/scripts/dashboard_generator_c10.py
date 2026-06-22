# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin10:
    def print_summary(self, dashboard_spec: Dict[str, Any]):
        """Print human-readable summary of dashboard specification."""
        metadata = dashboard_spec['metadata']
        service = metadata['service']
        config = dashboard_spec['configuration']
        panels = dashboard_spec['panels']
        
        print(f"\n{'='*60}")
        print(f"DASHBOARD SPECIFICATION SUMMARY")
        print(f"{'='*60}")
        
        print(f"\nDashboard Details:")
        print(f"  Title: {metadata['title']}")
        print(f"  Target Role: {metadata['target_role'].upper()}")
        print(f"  Service: {service['name']} ({service['type']})")
        print(f"  Criticality: {service['criticality']}")
        print(f"  Generated: {metadata['generated_at']}")
        
        print(f"\nConfiguration:")
        print(f"  Default Time Range: {config['default_time_range']}")
        print(f"  Refresh Interval: {config['refresh_interval']}")
        print(f"  Available Time Ranges: {', '.join(config['time_ranges'])}")
        
        print(f"\nPanels ({len(panels)}):")
        panel_types = {}
        for panel in panels:
            panel_type = panel['type']
            panel_types[panel_type] = panel_types.get(panel_type, 0) + 1
        
        for panel_type, count in panel_types.items():
            print(f"  {panel_type}: {count}")
        
        variables = dashboard_spec.get('variables', [])
        print(f"\nTemplate Variables ({len(variables)}):")
        for var in variables:
            print(f"  {var['name']} ({var['type']})")
        
        drill_downs = dashboard_spec.get('drill_down_paths', {})
        print(f"\nDrill-down Paths: {len(drill_downs)}")
        
        print(f"\nKey Features:")
        print(f"  • Golden Signals monitoring")
        print(f"  • Resource utilization tracking")
        print(f"  • Alert integration")
        print(f"  • Role-optimized layout")
        print(f"  • Service-type specific panels")
        
        print(f"\n{'='*60}\n")
