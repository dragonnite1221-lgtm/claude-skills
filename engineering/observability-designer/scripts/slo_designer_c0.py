# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


class SLODesignerMixin0:
    """Design and generate SLO frameworks for services."""
    SLO_TARGETS = {
        'critical': {
            'availability': 0.9999,  # 99.99% - 4.38 minutes downtime/month
            'latency_p95': 100,      # 95th percentile latency in ms
            'latency_p99': 500,      # 99th percentile latency in ms
            'error_rate': 0.001      # 0.1% error rate
        },
        'high': {
            'availability': 0.999,   # 99.9% - 43.8 minutes downtime/month
            'latency_p95': 200,      # 95th percentile latency in ms
            'latency_p99': 1000,     # 99th percentile latency in ms
            'error_rate': 0.005      # 0.5% error rate
        },
        'medium': {
            'availability': 0.995,   # 99.5% - 3.65 hours downtime/month
            'latency_p95': 500,      # 95th percentile latency in ms
            'latency_p99': 2000,     # 99th percentile latency in ms
            'error_rate': 0.01       # 1% error rate
        },
        'low': {
            'availability': 0.99,    # 99% - 7.3 hours downtime/month
            'latency_p95': 1000,     # 95th percentile latency in ms
            'latency_p99': 5000,     # 99th percentile latency in ms
            'error_rate': 0.02       # 2% error rate
        }
    }
    BURN_RATE_WINDOWS = [
        {'short': '5m', 'long': '1h', 'burn_rate': 14.4, 'budget_consumed': '2%'},
        {'short': '30m', 'long': '6h', 'burn_rate': 6, 'budget_consumed': '5%'},
        {'short': '2h', 'long': '1d', 'burn_rate': 3, 'budget_consumed': '10%'},
        {'short': '6h', 'long': '3d', 'burn_rate': 1, 'budget_consumed': '10%'}
    ]
    SERVICE_TYPE_SLIS = {
        'api': ['availability', 'latency', 'error_rate', 'throughput'],
        'web': ['availability', 'latency', 'error_rate', 'page_load_time'],
        'database': ['availability', 'query_latency', 'connection_success_rate', 'replication_lag'],
        'queue': ['availability', 'message_processing_time', 'queue_depth', 'message_loss_rate'],
        'batch': ['job_success_rate', 'job_duration', 'data_freshness', 'resource_utilization'],
        'ml': ['model_accuracy', 'prediction_latency', 'training_success_rate', 'feature_freshness']
    }
    def __init__(self):
        """Initialize the SLO Designer."""
        self.service_config = {}
        self.slo_framework = {}
    def load_service_definition(self, file_path: str) -> Dict[str, Any]:
        """Load service definition from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Service definition file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in service definition: {e}")
    def create_service_definition(self, service_type: str, criticality: str, 
                                user_facing: bool, name: str = None) -> Dict[str, Any]:
        """Create a service definition from parameters."""
        return {
            'name': name or f'{service_type}_service',
            'type': service_type,
            'criticality': criticality,
            'user_facing': user_facing,
            'description': f'A {criticality} criticality {service_type} service',
            'dependencies': [],
            'team': 'platform',
            'environment': 'production'
        }
    def generate_slis(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Service Level Indicators based on service characteristics."""
        service_type = service_def.get('type', 'api')
        base_slis = self.SERVICE_TYPE_SLIS.get(service_type, ['availability', 'latency', 'error_rate'])
        
        slis = []
        
        for sli_name in base_slis:
            sli = self._create_sli_definition(sli_name, service_def)
            if sli:
                slis.append(sli)
        
        # Add user-facing specific SLIs
        if service_def.get('user_facing', False):
            user_slis = self._generate_user_facing_slis(service_def)
            slis.extend(user_slis)
            
        return slis
    def _create_sli_definition(self, sli_name: str, service_def: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed SLI definition."""
        service_name = service_def.get('name', 'service')
        
        sli_definitions = {
            'availability': {
                'name': 'Availability',
                'description': 'Percentage of successful requests',
                'type': 'ratio',
                'good_events': f'sum(rate(http_requests_total{{service="{service_name}",code!~"5.."}}))',
                'total_events': f'sum(rate(http_requests_total{{service="{service_name}"}}))',
                'unit': 'percentage'
            },
            'latency': {
                'name': 'Request Latency P95',
                'description': '95th percentile of request latency',
                'type': 'threshold',
                'query': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[5m]))',
                'unit': 'seconds'
            },
            'error_rate': {
                'name': 'Error Rate',
                'description': 'Rate of 5xx errors',
                'type': 'ratio',
                'good_events': f'sum(rate(http_requests_total{{service="{service_name}",code!~"5.."}}))',
                'total_events': f'sum(rate(http_requests_total{{service="{service_name}"}}))',
                'unit': 'percentage'
            },
            'throughput': {
                'name': 'Request Throughput',
                'description': 'Requests per second',
                'type': 'gauge',
                'query': f'sum(rate(http_requests_total{{service="{service_name}"}}[5m]))',
                'unit': 'requests/sec'
            },
            'page_load_time': {
                'name': 'Page Load Time P95',
                'description': '95th percentile of page load time',
                'type': 'threshold',
                'query': f'histogram_quantile(0.95, rate(page_load_duration_seconds_bucket{{service="{service_name}"}}[5m]))',
                'unit': 'seconds'
            },
            'query_latency': {
                'name': 'Database Query Latency P95',
                'description': '95th percentile of database query latency',
                'type': 'threshold',
                'query': f'histogram_quantile(0.95, rate(db_query_duration_seconds_bucket{{service="{service_name}"}}[5m]))',
                'unit': 'seconds'
            },
            'connection_success_rate': {
                'name': 'Database Connection Success Rate',
                'description': 'Percentage of successful database connections',
                'type': 'ratio',
                'good_events': f'sum(rate(db_connections_total{{service="{service_name}",status="success"}}[5m]))',
                'total_events': f'sum(rate(db_connections_total{{service="{service_name}"}}[5m]))',
                'unit': 'percentage'
            }
        }
        
        return sli_definitions.get(sli_name)
