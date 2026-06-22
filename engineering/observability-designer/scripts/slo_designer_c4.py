# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


class SLODesignerMixin4:
    def _generate_monitoring_recommendations(self, service_def: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monitoring tool recommendations."""
        service_type = service_def.get('type', 'api')
        
        recommendations = {
            'metrics': {
                'collection': 'Prometheus with service discovery',
                'retention': '90 days for raw metrics, 1 year for aggregated',
                'alerting': 'Prometheus Alertmanager with multi-window burn rate alerts'
            },
            'logging': {
                'format': 'Structured JSON logs with correlation IDs',
                'aggregation': 'ELK stack or equivalent with proper indexing',
                'retention': '30 days for debug logs, 90 days for error logs'
            },
            'tracing': {
                'sampling': 'Adaptive sampling with 1% base rate',
                'storage': 'Jaeger or Zipkin with 7-day retention',
                'integration': 'OpenTelemetry instrumentation'
            }
        }
        
        if service_type == 'web':
            recommendations['synthetic_monitoring'] = {
                'frequency': 'Every 1 minute from 3+ geographic locations',
                'checks': 'Full user journey simulation',
                'tools': 'Pingdom, DataDog Synthetics, or equivalent'
            }
        
        return recommendations
    def _generate_implementation_guide(self, service_def: Dict[str, Any], 
                                     slis: List[Dict[str, Any]], 
                                     slos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate implementation guide for the SLO framework."""
        return {
            'prerequisites': [
                'Service instrumented with metrics collection (Prometheus format)',
                'Structured logging with correlation IDs',
                'Monitoring infrastructure (Prometheus, Grafana, Alertmanager)',
                'Incident response processes and escalation policies'
            ],
            'implementation_steps': [
                {
                    'step': 1,
                    'title': 'Instrument Service',
                    'description': 'Add metrics collection for all defined SLIs',
                    'estimated_effort': '1-2 days'
                },
                {
                    'step': 2,
                    'title': 'Configure Recording Rules',
                    'description': 'Set up Prometheus recording rules for SLI calculations',
                    'estimated_effort': '4-8 hours'
                },
                {
                    'step': 3,
                    'title': 'Implement Burn Rate Alerts',
                    'description': 'Configure multi-window burn rate alerting rules',
                    'estimated_effort': '1 day'
                },
                {
                    'step': 4,
                    'title': 'Create SLO Dashboard',
                    'description': 'Build Grafana dashboard for SLO tracking and error budget monitoring',
                    'estimated_effort': '4-6 hours'
                },
                {
                    'step': 5,
                    'title': 'Test and Validate',
                    'description': 'Test alerting and validate SLI measurements against expectations',
                    'estimated_effort': '1-2 days'
                },
                {
                    'step': 6,
                    'title': 'Documentation and Training',
                    'description': 'Document runbooks and train team on SLO monitoring',
                    'estimated_effort': '1 day'
                }
            ],
            'validation_checklist': [
                'All SLIs produce expected metric values',
                'Burn rate alerts fire correctly during simulated outages',
                'Error budget calculations match manual verification',
                'Dashboard displays accurate SLO achievement rates',
                'Alert routing reaches correct escalation paths',
                'Runbooks are complete and tested'
            ]
        }
    def export_json(self, framework: Dict[str, Any], output_file: str):
        """Export framework as JSON."""
        with open(output_file, 'w') as f:
            json.dump(framework, f, indent=2)
