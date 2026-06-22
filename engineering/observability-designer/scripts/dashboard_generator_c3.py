# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin3:
    def _create_golden_signals_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create golden signals monitoring panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'latency',
                'title': 'Request Latency',
                'type': 'timeseries',
                'grid_pos': {'x': 0, 'y': 8, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[5m])) * 1000',
                        'legendFormat': 'P50 Latency'
                    },
                    {
                        'expr': f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[5m])) * 1000',
                        'legendFormat': 'P95 Latency'
                    },
                    {
                        'expr': f'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{{service="{service_name}"}}[5m])) * 1000',
                        'legendFormat': 'P99 Latency'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'unit': 'ms',
                        'custom': {
                            'drawStyle': 'line',
                            'lineInterpolation': 'linear',
                            'lineWidth': 1,
                            'fillOpacity': 10
                        }
                    }
                },
                'options': {
                    'tooltip': {'mode': 'multi', 'sort': 'desc'},
                    'legend': {'displayMode': 'table', 'placement': 'bottom'}
                }
            },
            {
                'id': 'traffic',
                'title': 'Request Rate',
                'type': 'timeseries',
                'grid_pos': {'x': 12, 'y': 8, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'sum(rate(http_requests_total{{service="{service_name}"}}[5m]))',
                        'legendFormat': 'Total RPS'
                    },
                    {
                        'expr': f'sum(rate(http_requests_total{{service="{service_name}",code=~"2.."}}[5m]))',
                        'legendFormat': '2xx RPS'
                    },
                    {
                        'expr': f'sum(rate(http_requests_total{{service="{service_name}",code=~"4.."}}[5m]))',
                        'legendFormat': '4xx RPS'
                    },
                    {
                        'expr': f'sum(rate(http_requests_total{{service="{service_name}",code=~"5.."}}[5m]))',
                        'legendFormat': '5xx RPS'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'unit': 'reqps',
                        'custom': {
                            'drawStyle': 'line',
                            'lineInterpolation': 'linear',
                            'lineWidth': 1,
                            'fillOpacity': 0
                        }
                    }
                },
                'options': {
                    'tooltip': {'mode': 'multi', 'sort': 'desc'},
                    'legend': {'displayMode': 'table', 'placement': 'bottom'}
                }
            },
            {
                'id': 'errors',
                'title': 'Error Rate',
                'type': 'timeseries',
                'grid_pos': {'x': 0, 'y': 14, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'sum(rate(http_requests_total{{service="{service_name}",code=~"5.."}}[5m])) / sum(rate(http_requests_total{{service="{service_name}"}}[5m])) * 100',
                        'legendFormat': '5xx Error Rate'
                    },
                    {
                        'expr': f'sum(rate(http_requests_total{{service="{service_name}",code=~"4.."}}[5m])) / sum(rate(http_requests_total{{service="{service_name}"}}[5m])) * 100',
                        'legendFormat': '4xx Error Rate'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'unit': 'percent',
                        'custom': {
                            'drawStyle': 'line',
                            'lineInterpolation': 'linear',
                            'lineWidth': 2,
                            'fillOpacity': 20
                        }
                    },
                    'overrides': [
                        {
                            'matcher': {'id': 'byName', 'options': '5xx Error Rate'},
                            'properties': [{'id': 'color', 'value': {'fixedColor': 'red'}}]
                        }
                    ]
                },
                'options': {
                    'tooltip': {'mode': 'multi', 'sort': 'desc'},
                    'legend': {'displayMode': 'table', 'placement': 'bottom'}
                }
            },
            {
                'id': 'saturation',
                'title': 'Saturation Metrics',
                'type': 'timeseries',
                'grid_pos': {'x': 12, 'y': 14, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'rate(process_cpu_seconds_total{{service="{service_name}"}}[5m]) * 100',
                        'legendFormat': 'CPU Usage %'
                    },
                    {
                        'expr': f'process_resident_memory_bytes{{service="{service_name}"}} / process_virtual_memory_max_bytes{{service="{service_name}"}} * 100',
                        'legendFormat': 'Memory Usage %'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'unit': 'percent',
                        'max': 100,
                        'custom': {
                            'drawStyle': 'line',
                            'lineInterpolation': 'linear',
                            'lineWidth': 1,
                            'fillOpacity': 10
                        }
                    }
                },
                'options': {
                    'tooltip': {'mode': 'multi', 'sort': 'desc'},
                    'legend': {'displayMode': 'table', 'placement': 'bottom'}
                }
            }
        ]
