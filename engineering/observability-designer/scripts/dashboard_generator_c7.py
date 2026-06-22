# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin7:
    def _create_business_metrics_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create business metrics panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'business_kpis',
                'title': 'Business KPIs',
                'type': 'stat',
                'grid_pos': {'x': 0, 'y': 30, 'w': 24, 'h': 4},
                'targets': [
                    {
                        'expr': f'rate(business_transactions_total{{service="{service_name}"}}[1h])',
                        'legendFormat': 'Transactions/hour'
                    },
                    {
                        'expr': f'avg(business_transaction_value{{service="{service_name}"}}) * rate(business_transactions_total{{service="{service_name}"}}[1h])',
                        'legendFormat': 'Revenue/hour'
                    },
                    {
                        'expr': f'rate(user_registrations_total{{service="{service_name}"}}[1h])',
                        'legendFormat': 'New Users/hour'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'custom': {
                            'displayMode': 'basic'
                        }
                    }
                },
                'options': {
                    'orientation': 'horizontal',
                    'textMode': 'value_and_name'
                }
            }
        ]
    def _create_capacity_panels(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create capacity planning panels."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'id': 'capacity_trends',
                'title': 'Capacity Trends (7d)',
                'type': 'timeseries',
                'grid_pos': {'x': 0, 'y': 34, 'w': 24, 'h': 6},
                'targets': [
                    {
                        'expr': f'predict_linear(avg_over_time(rate(http_requests_total{{service="{service_name}"}}[5m])[7d:1h]), 7*24*3600)',
                        'legendFormat': 'Predicted Traffic (7d)'
                    },
                    {
                        'expr': f'predict_linear(avg_over_time(process_resident_memory_bytes{{service="{service_name}"}}[7d:1h]), 7*24*3600)',
                        'legendFormat': 'Predicted Memory Usage (7d)'
                    }
                ],
                'field_config': {
                    'defaults': {
                        'color': {'mode': 'palette-classic'},
                        'custom': {
                            'drawStyle': 'line',
                            'lineStyle': {'dash': [10, 10]}
                        }
                    }
                }
            }
        ]
    def _generate_template_variables(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate template variables for dynamic dashboard filtering."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'name': 'environment',
                'type': 'query',
                'query': 'label_values(environment)',
                'current': {'text': 'production', 'value': 'production'},
                'includeAll': False,
                'multi': False,
                'refresh': 'on_dashboard_load'
            },
            {
                'name': 'instance',
                'type': 'query',
                'query': f'label_values(up{{service="{service_name}"}}, instance)',
                'current': {'text': 'All', 'value': '$__all'},
                'includeAll': True,
                'multi': True,
                'refresh': 'on_time_range_change'
            },
            {
                'name': 'handler',
                'type': 'query',
                'query': f'label_values(http_requests_total{{service="{service_name}"}}, handler)',
                'current': {'text': 'All', 'value': '$__all'},
                'includeAll': True,
                'multi': True,
                'refresh': 'on_time_range_change'
            }
        ]
