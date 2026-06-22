# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin0:
    """Generate comprehensive dashboard specifications."""
    ROLE_LAYOUTS = {
        'sre': {
            'primary_focus': ['availability', 'latency', 'errors', 'resource_utilization'],
            'secondary_focus': ['throughput', 'capacity', 'dependencies'],
            'time_ranges': ['1h', '6h', '1d', '7d'],
            'default_refresh': '30s'
        },
        'developer': {
            'primary_focus': ['latency', 'errors', 'throughput', 'business_metrics'],
            'secondary_focus': ['resource_utilization', 'dependencies'],
            'time_ranges': ['15m', '1h', '6h', '1d'],
            'default_refresh': '1m'
        },
        'executive': {
            'primary_focus': ['availability', 'business_metrics', 'user_experience'],
            'secondary_focus': ['cost', 'capacity_trends'],
            'time_ranges': ['1d', '7d', '30d'],
            'default_refresh': '5m'
        },
        'ops': {
            'primary_focus': ['resource_utilization', 'capacity', 'alerts', 'deployments'],
            'secondary_focus': ['throughput', 'latency'],
            'time_ranges': ['5m', '30m', '2h', '1d'],
            'default_refresh': '15s'
        }
    }
    SERVICE_METRICS = {
        'api': {
            'golden_signals': ['latency', 'traffic', 'errors', 'saturation'],
            'key_metrics': [
                'http_requests_total',
                'http_request_duration_seconds',
                'http_request_size_bytes',
                'http_response_size_bytes'
            ],
            'resource_metrics': ['cpu_usage', 'memory_usage', 'goroutines']
        },
        'web': {
            'golden_signals': ['latency', 'traffic', 'errors', 'saturation'],
            'key_metrics': [
                'http_requests_total',
                'http_request_duration_seconds',
                'page_load_time',
                'user_sessions'
            ],
            'resource_metrics': ['cpu_usage', 'memory_usage', 'connections']
        },
        'database': {
            'golden_signals': ['latency', 'traffic', 'errors', 'saturation'],
            'key_metrics': [
                'db_connections_active',
                'db_query_duration_seconds',
                'db_queries_total',
                'db_slow_queries_total'
            ],
            'resource_metrics': ['cpu_usage', 'memory_usage', 'disk_io', 'connections']
        },
        'queue': {
            'golden_signals': ['latency', 'traffic', 'errors', 'saturation'],
            'key_metrics': [
                'queue_depth',
                'message_processing_duration',
                'messages_published_total',
                'messages_consumed_total'
            ],
            'resource_metrics': ['cpu_usage', 'memory_usage', 'disk_usage']
        }
    }
    VISUALIZATION_TYPES = {
        'latency': 'line_chart',
        'throughput': 'line_chart',
        'error_rate': 'line_chart',
        'success_rate': 'stat',
        'resource_utilization': 'gauge',
        'queue_depth': 'bar_chart',
        'status': 'stat',
        'distribution': 'heatmap',
        'alerts': 'table',
        'logs': 'logs_panel'
    }
    def __init__(self):
        """Initialize the Dashboard Generator."""
        self.service_config = {}
        self.dashboard_spec = {}
    def load_service_definition(self, file_path: str) -> Dict[str, Any]:
        """Load service definition from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Service definition file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in service definition: {e}")
    def create_service_definition(self, service_type: str, name: str, 
                                criticality: str = 'medium') -> Dict[str, Any]:
        """Create a service definition from parameters."""
        return {
            'name': name,
            'type': service_type,
            'criticality': criticality,
            'description': f'{name} - A {criticality} criticality {service_type} service',
            'team': 'platform',
            'environment': 'production',
            'dependencies': [],
            'tags': []
        }
    def generate_dashboard_specification(self, service_def: Dict[str, Any], 
                                       target_role: str = 'sre') -> Dict[str, Any]:
        """Generate comprehensive dashboard specification."""
        service_name = service_def.get('name', 'Service')
        service_type = service_def.get('type', 'api')
        
        # Get role-specific configuration
        role_config = self.ROLE_LAYOUTS.get(target_role, self.ROLE_LAYOUTS['sre'])
        
        dashboard_spec = {
            'metadata': {
                'title': f"{service_name} - {target_role.upper()} Dashboard",
                'service': service_def,
                'target_role': target_role,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'version': '1.0'
            },
            'configuration': {
                'time_ranges': role_config['time_ranges'],
                'default_time_range': role_config['time_ranges'][1],  # Second option as default
                'refresh_interval': role_config['default_refresh'],
                'timezone': 'UTC',
                'theme': 'dark'
            },
            'layout': self._generate_dashboard_layout(service_def, role_config),
            'panels': self._generate_panels(service_def, role_config),
            'variables': self._generate_template_variables(service_def),
            'alerts_integration': self._generate_alerts_integration(service_def),
            'drill_down_paths': self._generate_drill_down_paths(service_def)
        }
        
        return dashboard_spec
    def _generate_dashboard_layout(self, service_def: Dict[str, Any], 
                                 role_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dashboard layout configuration."""
        return {
            'grid_settings': {
                'width': 24,  # Grafana-style 24-column grid
                'height_unit': 'px',
                'cell_height': 30
            },
            'sections': [
                {
                    'title': 'Service Overview',
                    'collapsed': False,
                    'y_position': 0,
                    'panels': ['service_status', 'slo_summary', 'error_budget']
                },
                {
                    'title': 'Golden Signals',
                    'collapsed': False,
                    'y_position': 8,
                    'panels': ['latency', 'traffic', 'errors', 'saturation']
                },
                {
                    'title': 'Resource Utilization',
                    'collapsed': False,
                    'y_position': 16,
                    'panels': ['cpu_usage', 'memory_usage', 'network_io', 'disk_io']
                },
                {
                    'title': 'Dependencies & Downstream',
                    'collapsed': True,
                    'y_position': 24,
                    'panels': ['dependency_status', 'downstream_latency', 'circuit_breakers']
                }
            ]
        }
