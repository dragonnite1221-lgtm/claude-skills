# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


class SLODesignerMixin1:
    def _generate_user_facing_slis(self, service_def: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate additional SLIs for user-facing services."""
        service_name = service_def.get('name', 'service')
        
        return [
            {
                'name': 'User Journey Success Rate',
                'description': 'Percentage of successful complete user journeys',
                'type': 'ratio',
                'good_events': f'sum(rate(user_journey_total{{service="{service_name}",status="success"}}[5m]))',
                'total_events': f'sum(rate(user_journey_total{{service="{service_name}"}}[5m]))',
                'unit': 'percentage'
            },
            {
                'name': 'Feature Availability',
                'description': 'Percentage of time key features are available',
                'type': 'ratio',
                'good_events': f'sum(rate(feature_checks_total{{service="{service_name}",status="available"}}[5m]))',
                'total_events': f'sum(rate(feature_checks_total{{service="{service_name}"}}[5m]))',
                'unit': 'percentage'
            }
        ]
    def generate_slos(self, service_def: Dict[str, Any], slis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate Service Level Objectives based on service criticality."""
        criticality = service_def.get('criticality', 'medium')
        targets = self.SLO_TARGETS.get(criticality, self.SLO_TARGETS['medium'])
        
        slos = []
        
        for sli in slis:
            slo = self._create_slo_from_sli(sli, targets, service_def)
            if slo:
                slos.append(slo)
                
        return slos
    def _create_slo_from_sli(self, sli: Dict[str, Any], targets: Dict[str, float], 
                           service_def: Dict[str, Any]) -> Dict[str, Any]:
        """Create SLO definition from SLI."""
        sli_name = sli['name'].lower().replace(' ', '_')
        
        # Map SLI names to target keys
        target_mapping = {
            'availability': 'availability',
            'request_latency_p95': 'latency_p95',
            'error_rate': 'error_rate',
            'user_journey_success_rate': 'availability',
            'feature_availability': 'availability',
            'page_load_time_p95': 'latency_p95',
            'database_query_latency_p95': 'latency_p95',
            'database_connection_success_rate': 'availability'
        }
        
        target_key = target_mapping.get(sli_name)
        if not target_key:
            return None
            
        target_value = targets.get(target_key)
        if target_value is None:
            return None
            
        # Determine comparison operator and format target
        if 'latency' in sli_name or 'duration' in sli_name:
            operator = '<='
            target_display = f"{target_value}ms" if target_value < 10 else f"{target_value/1000}s"
        elif 'rate' in sli_name and 'error' in sli_name:
            operator = '<='
            target_display = f"{target_value * 100}%"
            target_value = target_value  # Keep as decimal
        else:
            operator = '>='
            target_display = f"{target_value * 100}%"
        
        # Calculate time windows
        time_windows = ['1h', '1d', '7d', '30d']
        
        slo = {
            'name': f"{sli['name']} SLO",
            'description': f"Service level objective for {sli['description'].lower()}",
            'sli_name': sli['name'],
            'target_value': target_value,
            'target_display': target_display,
            'operator': operator,
            'time_windows': time_windows,
            'measurement_window': '30d',
            'service': service_def.get('name', 'service'),
            'criticality': service_def.get('criticality', 'medium')
        }
        
        return slo
