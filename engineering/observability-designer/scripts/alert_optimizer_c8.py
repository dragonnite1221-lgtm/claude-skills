# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin8:
    def _remove_duplicate_alerts(self, alerts: List[Dict[str, Any]], 
                               duplicates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate alerts from the list."""
        indices_to_remove = set()
        
        for duplicate_group in duplicates:
            if duplicate_group['type'] == 'exact_duplicate':
                # Keep the first alert, remove the rest
                alert_indices = [alert_info['index'] for alert_info in duplicate_group['alerts']]
                indices_to_remove.update(alert_indices[1:])  # Remove all but first
        
        return [alert for i, alert in enumerate(alerts) if i not in indices_to_remove]
    def _generate_missing_alerts(self, coverage_gaps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts for missing coverage."""
        new_alerts = []
        
        for missing_signal in coverage_gaps.get('missing_golden_signals', []):
            if missing_signal == 'latency':
                new_alert = {
                    'alert': 'HighLatency',
                    'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5',
                    'for': '5m',
                    'labels': {
                        'severity': 'warning'
                    },
                    'annotations': {
                        'summary': 'High request latency detected',
                        'description': 'The 95th percentile latency is above 500ms for 5 minutes.',
                        'generated': 'true'
                    }
                }
                new_alerts.append(new_alert)
            
            elif missing_signal == 'errors':
                new_alert = {
                    'alert': 'HighErrorRate',
                    'expr': 'sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.01',
                    'for': '5m',
                    'labels': {
                        'severity': 'warning'
                    },
                    'annotations': {
                        'summary': 'High error rate detected',
                        'description': 'Error rate is above 1% for 5 minutes.',
                        'generated': 'true'
                    }
                }
                new_alerts.append(new_alert)
        
        return new_alerts
    def analyze_configuration(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis of alert configuration."""
        alerts = alert_config.get('alerts', alert_config.get('rules', []))
        services = alert_config.get('services', [])
        
        analysis_results = {
            'summary': {
                'total_alerts': len(alerts),
                'analysis_timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            'noisy_alerts': self.analyze_alert_noise(alerts),
            'coverage_gaps': self.identify_coverage_gaps(alerts, services),
            'duplicate_alerts': self.find_duplicate_alerts(alerts),
            'threshold_analysis': self.analyze_thresholds(alerts),
            'alert_fatigue_assessment': self.assess_alert_fatigue_risk(alerts)
        }
        
        # Generate overall recommendations
        analysis_results['overall_recommendations'] = self._generate_overall_recommendations(analysis_results)
        
        return analysis_results
    def _generate_overall_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on complete analysis."""
        recommendations = []
        
        # High-priority recommendations
        if analysis_results['alert_fatigue_assessment']['risk_level'] == 'high':
            recommendations.append("HIGH PRIORITY: Address alert fatigue risk by reducing alert volume")
        
        if len(analysis_results['coverage_gaps']['critical_gaps']) > 0:
            recommendations.append("HIGH PRIORITY: Address critical monitoring gaps")
        
        # Medium-priority recommendations
        if len(analysis_results['noisy_alerts']) > 0:
            recommendations.append(f"Optimize {len(analysis_results['noisy_alerts'])} noisy alerts to reduce false positives")
        
        if len(analysis_results['duplicate_alerts']) > 0:
            recommendations.append(f"Remove or consolidate {len(analysis_results['duplicate_alerts'])} duplicate alert groups")
        
        # General recommendations
        recommendations.append("Implement proper alert routing and escalation policies")
        recommendations.append("Create runbooks for all production alerts")
        recommendations.append("Set up alert effectiveness monitoring and regular reviews")
        
        return recommendations
    def export_analysis(self, analysis_results: Dict[str, Any], output_file: str, 
                       format_type: str = 'json'):
        """Export analysis results."""
        if format_type.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(analysis_results, f, indent=2)
        elif format_type.lower() == 'html':
            self._export_html_report(analysis_results, output_file)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    def _export_html_report(self, analysis_results: Dict[str, Any], output_file: str):
        """Export analysis as HTML report."""
        html_content = self._generate_html_report(analysis_results)
        with open(output_file, 'w') as f:
            f.write(html_content)
