# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin6:
    def _create_database_specific_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create database-specific panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'db_connections',
                'title': 'Database Connections',
                'type': 'timeseries',
                'grid_pos': {'x': 0, 'y': 24, 'w': 8, 'h': 6},
                'targets': [
                    {
                        'expr': f'db_connections_active{{service="{service_name}"}}',
                        'legendFormat': 'Active Connections'
                    },
                    {
                        'expr': f'db_connections_idle{{service="{service_name}"}}',
                        'legendFormat': 'Idle Connections'
                    },
                    {
                        'expr': f'db_connections_max{{service="{service_name}"}}',
                        'legendFormat': 'Max Connections'
                    }
                ]
            },
            {
                'id': 'query_performance',
                'title': 'Query Performance',
                'type': 'timeseries',
                'grid_pos': {'x': 8, 'y': 24, 'w': 8, 'h': 6},
                'targets': [
                    {
                        'expr': f'rate(db_queries_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'Queries/sec'
                    },
                    {
                        'expr': f'rate(db_slow_queries_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'Slow Queries/sec'
                    }
                ]
            },
            {
                'id': 'db_locks',
                'title': 'Database Locks',
                'type': 'stat',
                'grid_pos': {'x': 16, 'y': 24, 'w': 8, 'h': 6},
                'targets': [
                    {
                        'expr': f'db_locks_waiting{{service="{service_name}"}}',
                        'legendFormat': 'Waiting Locks'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'thresholds'},
                        'thresholds': {
                            'steps': [
                                {'color': 'green', 'value': 0},
                                {'color': 'yellow', 'value': 1},
                                {'color': 'red', 'value': 5}
                            ]
                        }
                    }
                }
            }
        ]
    def _create_queue_specific_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create queue-specific panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'queue_depth',
                'title': 'Queue Depth',
                'type': 'timeseries',
                'grid_pos': {'x': 0, 'y': 24, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'queue_depth{{service="{service_name}"}}',
                        'legendFormat': 'Messages in Queue'
                    }
                ]
            },
            {
                'id': 'message_throughput',
                'title': 'Message Throughput',
                'type': 'timeseries',
                'grid_pos': {'x': 12, 'y': 24, 'w': 12, 'h': 6},
                'targets': [
                    {
                        'expr': f'rate(messages_published_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'Published/sec'
                    },
                    {
                        'expr': f'rate(messages_consumed_total{{service="{service_name}"}}[5m])',
                        'legendFormat': 'Consumed/sec'
                    }
                ]
            }
        ]
