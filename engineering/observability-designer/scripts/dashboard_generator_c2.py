# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin2:
    def _create_overview_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create service overview panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'service_status',
                'title': 'Service Status',
                'type': 'stat',
                'grid_pos': {'x': 0, 'y': 0, 'w': 6, 'h': 4},
                'targets': [
                    {
                        'expr': f'up{{service="{service_name}"}}',
                        'legendFormat': 'Status'
                    }
                ],
                'field_config': {
                    'overrides': [
                        {
                            'matcher': {'id': 'byName', 'options': 'Status'},
                            'properties': [
                                {'id': 'color', 'value': {'mode': 'thresholds'}},
                                {'id': 'thresholds', 'value': {
                                    'steps': [
                                        {'color': 'red', 'value': 0},
                                        {'color': 'green', 'value': 1}
                                    ]
                                }},
                                {'id': 'mappings', 'value': [
                                    {'options': {'0': {'text': 'DOWN'}}, 'type': 'value'},
                                    {'options': {'1': {'text': 'UP'}}, 'type': 'value'}
                                ]}
                            ]
                        }
                    ]
                },
                'options': {
                    'orientation': 'horizontal',
                    'textMode': 'value_and_name'
                }
            },
            {
                'id': 'slo_summary',
                'title': 'SLO Achievement (30d)',
                'type': 'stat',
                'grid_pos': {'x': 6, 'y': 0, 'w': 9, 'h': 4},
                'targets': [
                    {
                        'expr': f'(1 - (increase(http_requests_total{{service="{service_name}",code=~"5.."}}[30d]) / increase(http_requests_total{{service="{service_name}"}}[30d]))) * 100',
                        'legendFormat': 'Availability'
                    },
                    {
                        'expr': f'histogram_quantile(0.95, increase(http_request_duration_seconds_bucket{{service="{service_name}"}}[30d])) * 1000',
                        'legendFormat': 'P95 Latency (ms)'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'thresholds'},
                        'thresholds': {
                            'steps': [
                                {'color': 'red', 'value': 0},
                                {'color': 'yellow', 'value': 99.0},
                                {'color': 'green', 'value': 99.9}
                            ]
                        }
                    }
                },
                'options': {
                    'orientation': 'horizontal',
                    'textMode': 'value_and_name'
                }
            },
            {
                'id': 'error_budget',
                'title': 'Error Budget Remaining',
                'type': 'gauge',
                'grid_pos': {'x': 15, 'y': 0, 'w': 9, 'h': 4},
                'targets': [
                    {
                        'expr': f'(1 - (increase(http_requests_total{{service="{service_name}",code=~"5.."}}[30d]) / increase(http_requests_total{{service="{service_name}"}}[30d])) - 0.999) / 0.001 * 100',
                        'legendFormat': 'Error Budget %'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'thresholds'},
                        'min': 0,
                        'max': 100,
                        'thresholds': {
                            'steps': [
                                {'color': 'red', 'value': 0},
                                {'color': 'yellow', 'value': 25},
                                {'color': 'green', 'value': 50}
                            ]
                        },
                        'unit': 'percent'
                    }
                },
                'options': {
                    'showThresholdLabels': True,
                    'showThresholdMarkers': True
                }
            }
        ]
