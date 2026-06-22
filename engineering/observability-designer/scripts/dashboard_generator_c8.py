# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin8:
    def _generate_alerts_integration(self, service_def: Dict[str, Any]) -> Dict[str, Any]:
        """Generate alerts integration configuration."""
        service_name = service_def.get('name', 'service')
        
        return {
            'alert_annotations': True,
            'alert_rules_query': f'ALERTS{{service="{service_name}"}}',
            'alert_panels': [
                {
                    'title': 'Active Alerts',
                    'type': 'table',
                    'query': f'ALERTS{{service="{service_name}",alertstate="firing"}}',
                    'columns': ['alertname', 'severity', 'instance', 'description']
                }
            ]
        }
    def _generate_drill_down_paths(self, service_def: Dict[str, Any]) -> Dict[str, Any]:
        """Generate drill-down navigation paths."""
        service_name = service_def.get('name', 'service')
        
        return {
            'service_overview': {
                'from': 'service_status',
                'to': 'detailed_health_dashboard',
                'url': f'/d/service-health/{service_name}-health',
                'params': ['var-service', 'var-environment']
            },
            'error_investigation': {
                'from': 'errors',
                'to': 'error_details_dashboard',
                'url': f'/d/errors/{service_name}-errors',
                'params': ['var-service', 'var-time_range']
            },
            'latency_analysis': {
                'from': 'latency',
                'to': 'trace_analysis_dashboard',
                'url': f'/d/traces/{service_name}-traces',
                'params': ['var-service', 'var-handler']
            },
            'capacity_planning': {
                'from': 'saturation',
                'to': 'capacity_dashboard',
                'url': f'/d/capacity/{service_name}-capacity',
                'params': ['var-service', 'var-time_range']
            }
        }
    def generate_grafana_json(self, dashboard_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dashboard specification to Grafana JSON format."""
        metadata = dashboard_spec['metadata']
        config = dashboard_spec['configuration']
        
        grafana_json = {
            'dashboard': {
                'id': None,
                'title': metadata['title'],
                'tags': [metadata['service']['type'], metadata['target_role'], 'generated'],
                'timezone': config['timezone'],
                'refresh': config['refresh_interval'],
                'time': {
                    'from': 'now-1h',
                    'to': 'now'
                },
                'templating': {
                    'list': dashboard_spec['variables']
                },
                'panels': self._convert_panels_to_grafana_format(dashboard_spec['panels']),
                'version': 1,
                'schemaVersion': 30
            },
            'overwrite': True
        }
        
        return grafana_json
    def _convert_panels_to_grafana_format(self, panels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert panel specifications to Grafana format."""
        grafana_panels = []
        
        for panel in panels:
            grafana_panel = {
                'id': hash(panel['id']) % 1000,  # Generate numeric ID
                'title': panel['title'],
                'type': panel['type'],
                'gridPos': panel['grid_pos'],
                'targets': panel['targets'],
                'fieldConfig': panel.get('field_config', {}),
                'options': panel.get('options', {}),
                'transformations': panel.get('transformations', [])
            }
            grafana_panels.append(grafana_panel)
        
        return grafana_panels
