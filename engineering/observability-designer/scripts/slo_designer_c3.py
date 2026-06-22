# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


class SLODesignerMixin3:
    def generate_sla_recommendations(self, service_def: Dict[str, Any], 
                                   slos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SLA recommendations for customer-facing services."""
        if not service_def.get('user_facing', False):
            return {
                'applicable': False,
                'reason': 'SLA not recommended for non-user-facing services'
            }
        
        criticality = service_def.get('criticality', 'medium')
        
        # SLA targets should be more conservative than SLO targets
        sla_buffer = 0.001  # 0.1% buffer below SLO
        
        sla_recommendations = {
            'applicable': True,
            'service': service_def.get('name'),
            'commitments': [],
            'penalties': self._generate_penalty_structure(criticality),
            'measurement_methodology': 'External synthetic monitoring from multiple geographic locations',
            'exclusions': [
                'Planned maintenance windows (with 72h advance notice)',
                'Customer-side network or infrastructure issues',
                'Force majeure events',
                'Third-party service dependencies beyond our control'
            ]
        }
        
        for slo in slos:
            if slo['operator'] == '>=' and 'availability' in slo['sli_name'].lower():
                sla_target = max(0.9, slo['target_value'] - sla_buffer)
                commitment = {
                    'metric': slo['sli_name'],
                    'target': sla_target,
                    'target_display': f"{sla_target * 100:.2f}%",
                    'measurement_window': 'monthly',
                    'measurement_method': 'Uptime monitoring with 1-minute granularity'
                }
                sla_recommendations['commitments'].append(commitment)
        
        return sla_recommendations
    def _generate_penalty_structure(self, criticality: str) -> List[Dict[str, Any]]:
        """Generate penalty structure based on service criticality."""
        penalty_structures = {
            'critical': [
                {'breach_threshold': '< 99.99%', 'credit_percentage': 10},
                {'breach_threshold': '< 99.9%', 'credit_percentage': 25},
                {'breach_threshold': '< 99%', 'credit_percentage': 50}
            ],
            'high': [
                {'breach_threshold': '< 99.9%', 'credit_percentage': 10},
                {'breach_threshold': '< 99.5%', 'credit_percentage': 25}
            ],
            'medium': [
                {'breach_threshold': '< 99.5%', 'credit_percentage': 10}
            ],
            'low': []
        }
        
        return penalty_structures.get(criticality, [])
    def generate_framework(self, service_def: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete SLO framework."""
        # Generate SLIs
        slis = self.generate_slis(service_def)
        
        # Generate SLOs
        slos = self.generate_slos(service_def, slis)
        
        # Calculate error budgets
        error_budgets = self.calculate_error_budgets(slos)
        
        # Generate SLA recommendations
        sla_recommendations = self.generate_sla_recommendations(service_def, slos)
        
        # Create comprehensive framework
        framework = {
            'metadata': {
                'service': service_def,
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'framework_version': '1.0'
            },
            'slis': slis,
            'slos': slos,
            'error_budgets': error_budgets,
            'sla_recommendations': sla_recommendations,
            'monitoring_recommendations': self._generate_monitoring_recommendations(service_def),
            'implementation_guide': self._generate_implementation_guide(service_def, slis, slos)
        }
        
        return framework
