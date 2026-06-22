# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin5:
    def _create_api_specific_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create API-specific panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'endpoint_latency',
                'title': 'Top Slowest Endpoints',
                'type': 'table',
                'grid_pos': {'x': 0, 'y': 24, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'topk(10, histogram_quantile(0.95, sum by (handler) (rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[5m])))) * 1000',
                        'legendFormat': '{{handler}}',
                        'format': 'table',
                        'instant': True
                    }
                ],
                'transformations': [
                    {
                        'id': 'organize',
                        'options': {
                            'excludeByName': {'Time': True},
                            'renameByName': {'Value': 'P95 Latency (ms)'}
                        }
                    }
                ],
                'field_config': {
                    'overrides': [
                        {
                            'matcher': {'id': 'byName', 'options': 'P95 Latency (ms)'},
                            'properties': [
                                {'id': 'color', 'value': {'mode': 'thresholds'}},
                                {'id': 'thresholds', 'value': {
                                    'steps': [
                                        {'color': 'green', 'value': 0},
                                        {'color': 'yellow', 'value': 100},
                                        {'color': 'red', 'value': 500}
                                    ]
                                }}
                            ]
                        }
                    ]
                }
            },
            {
                'id': 'request_size_distribution',
                'title': 'Request Size Distribution',
                'type': 'heatmap',
                'grid_pos': {'x': 12, 'y': 24, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'sum by (le) (rate(http_request_size_bytes_bucket{{service="{service_name}"}}[5m]))',
                        'legendFormat': '{{le}}'
                    }
                ],
                'options': {
                    'calculate': True,
                    'yAxis': {'unit': 'bytes'},
                    'color': {'scheme': 'Spectral'}
                }
            }
        ]
