# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin4:
    def _create_resource_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create resource utilization panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'cpu_usage',
                'title': 'CPU Usage',
                'type': 'gauge',
                'grid_pos': {'x': 0, 'y': 20, 'w': 6, 'h': 4},
                'targets': [
                    {
                        'expr': f'rate(process_cpu_seconds_total{{service="{service_name}"}}[5m]) * 100',
                        'legendFormat': 'CPU %'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'thresholds'},
                        'unit': 'percent',
                        'min': 0,
                        'max': 100,
                        'thresholds': {
                            'steps': [
                                {'color': 'green', 'value': 0},
                                {'color': 'yellow', 'value': 70},
                                {'color': 'red', 'value': 90}
                            ]
                        }
                    }
                },
                'options': {
                    'showThresholdLabels': True,
                    'showThresholdMarkers': True
                }
            },
            {
                'id': 'memory_usage',
                'title': 'Memory Usage',
                'type': 'gauge',
                'grid_pos': {'x': 6, 'y': 20, 'w': 6, 'h': 4},
                'targets': [
                    {
                        'expr': f'process_resident_memory_bytes{{service="{service_name}"}} / 1024 / 1024',
                        'legendFormat': 'Memory MB'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'thresholds'},
                        'unit': 'decbytes',
                        'thresholds': {
                            'steps': [
                                {'color': 'green', 'value': 0},
                                {'color': 'yellow', 'value': 512000000},  # 512MB
                                {'color': 'red', 'value': 1024000000}     # 1GB
                            ]
                        }
                    }
                }
            },
            {
                'id': 'network_io',
                'title': 'Network I/O',
                'type': 'timeseries',
                'grid_pos': {'x': 12, 'y': 20, 'w': 6, 'h': 4},
                'targets': [
                    {
                        'expr': f'rate(process_network_receive_bytes_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'RX Bytes/s'
                    },
                    {
                        'expr': f'rate(process_network_transmit_bytes_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'TX Bytes/s'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'unit': 'binBps'
                    }
                }
            },
            {
                'id': 'disk_io',
                'title': 'Disk I/O',
                'type': 'timeseries',
                'grid_pos': {'x': 18, 'y': 20, 'w': 6, 'h': 4},
                'targets': [
                    {
                        'expr': f'rate(process_disk_read_bytes_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'Read Bytes/s'
                    },
                    {
                        'expr': f'rate(process_disk_write_bytes_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'Write Bytes/s'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'unit': 'binBps'
                    }
                }
            }
        ]
