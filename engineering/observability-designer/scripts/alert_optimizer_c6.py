# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin6:
    def assess_alert_fatigue_risk(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess risk of alert fatigue."""
        fatigue_assessment = {
            'total_alerts': len(alerts),
            'risk_level': 'low',
            'risk_factors': [],
            'metrics': {},
            'recommendations': []
        }
        
        # Count alerts by severity
        severity_counts = Counter()
        for alert in alerts:
            severity = alert.get('labels', {}).get('severity', 'unknown')
            severity_counts[severity] += 1
        
        fatigue_assessment['metrics']['severity_distribution'] = dict(severity_counts)
        
        # Calculate risk factors
        critical_count = severity_counts.get('critical', 0)
        warning_count = severity_counts.get('warning', 0) + severity_counts.get('high', 0)
        total_high_priority = critical_count + warning_count
        
        # Too many high-priority alerts
        if total_high_priority > 50:
            fatigue_assessment['risk_factors'].append('High number of critical/warning alerts')
            fatigue_assessment['recommendations'].append('Review and reduce number of high-priority alerts')
        
        # Poor critical to warning ratio
        if critical_count > 0 and warning_count > 0:
            critical_ratio = critical_count / (critical_count + warning_count)
            if critical_ratio > 0.3:  # More than 30% critical
                fatigue_assessment['risk_factors'].append('High ratio of critical alerts')
                fatigue_assessment['recommendations'].append('Review critical alert criteria - not everything should be critical')
        
        # Estimate daily alert volume
        daily_estimate = self._estimate_daily_alert_volume(alerts)
        fatigue_assessment['metrics']['estimated_daily_alerts'] = daily_estimate
        
        if daily_estimate > 100:
            fatigue_assessment['risk_factors'].append('High estimated daily alert volume')
            fatigue_assessment['recommendations'].append('Implement alert grouping and suppression rules')
        
        # Check for missing runbooks
        alerts_without_runbooks = [alert for alert in alerts 
                                 if not alert.get('annotations', {}).get('runbook_url')]
        runbook_ratio = len(alerts_without_runbooks) / len(alerts) if alerts else 0
        
        if runbook_ratio > 0.5:
            fatigue_assessment['risk_factors'].append('Many alerts lack runbooks')
            fatigue_assessment['recommendations'].append('Create runbooks for alerts to improve response efficiency')
        
        # Determine overall risk level
        risk_score = len(fatigue_assessment['risk_factors'])
        if risk_score >= 3:
            fatigue_assessment['risk_level'] = 'high'
        elif risk_score >= 1:
            fatigue_assessment['risk_level'] = 'medium'
        
        return fatigue_assessment
    def _estimate_daily_alert_volume(self, alerts: List[Dict[str, Any]]) -> int:
        """Estimate daily alert volume."""
        total_estimated = 0
        
        for alert in alerts:
            # Use historical data if available
            historical_data = alert.get('historical_data', {})
            if historical_data and 'fires_per_day' in historical_data:
                total_estimated += historical_data['fires_per_day']
                continue
            
            # Otherwise estimate based on alert characteristics
            expr = alert.get('expr', alert.get('condition', ''))
            severity = alert.get('labels', {}).get('severity', 'warning')
            
            # Base estimate by severity
            base_estimates = {
                'critical': 0.1,  # Critical should rarely fire
                'high': 0.5,
                'warning': 2,
                'info': 5
            }
            
            estimate = base_estimates.get(severity, 1)
            
            # Adjust based on alert type
            if 'error_rate' in expr.lower():
                estimate *= 1.5  # Error rate alerts tend to be more frequent
            elif 'availability' in expr.lower() or 'up' in expr.lower():
                estimate *= 0.5  # Availability alerts should be rare
            
            total_estimated += estimate
        
        return int(total_estimated)
