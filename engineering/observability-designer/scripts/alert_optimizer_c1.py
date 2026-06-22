# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin1:
    def _generate_noise_reduction_recommendations(self, alert: Dict[str, Any], 
                                                 reasons: List[str]) -> List[str]:
        """Generate recommendations to reduce alert noise."""
        recommendations = []
        
        if "No 'for' clause" in str(reasons):
            recommendations.append("Add 'for: 5m' clause to prevent flapping")
        
        if "Very short evaluation interval" in str(reasons):
            recommendations.append("Increase evaluation interval to at least 1 minute")
        
        if "sensitive threshold" in str(reasons):
            recommendations.append("Review and increase threshold based on historical data")
        
        if "High firing rate" in str(reasons):
            recommendations.append("Analyze historical firing patterns and adjust thresholds")
        
        if "High false positive rate" in str(reasons):
            recommendations.append("Implement more specific conditions to reduce false positives")
        
        if "noisy pattern" in str(reasons):
            recommendations.append("Consider using percentile-based thresholds instead of absolute values")
        
        return recommendations
    def identify_coverage_gaps(self, alerts: List[Dict[str, Any]], 
                             services: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Identify gaps in monitoring coverage."""
        coverage_analysis = {
            'missing_categories': [],
            'missing_golden_signals': [],
            'service_coverage_gaps': [],
            'critical_gaps': [],
            'recommendations': []
        }
        
        # Analyze coverage by category
        covered_categories = set()
        alert_categories = []
        
        for alert in alerts:
            alert_rule = alert.get('expr', alert.get('condition', ''))
            alert_name = alert.get('alert', alert.get('name', ''))
            
            category = self._classify_alert_category(alert_rule, alert_name)
            if category:
                covered_categories.add(category)
                alert_categories.append(category)
        
        # Check for missing essential categories
        missing_categories = set(self.COVERAGE_CATEGORIES) - covered_categories
        coverage_analysis['missing_categories'] = list(missing_categories)
        
        # Check for missing golden signals
        covered_signals = set()
        for alert in alerts:
            alert_rule = alert.get('expr', alert.get('condition', ''))
            signal = self._identify_golden_signal(alert_rule)
            if signal:
                covered_signals.add(signal)
        
        missing_signals = set(self.GOLDEN_SIGNALS) - covered_signals
        coverage_analysis['missing_golden_signals'] = list(missing_signals)
        
        # Analyze service-specific coverage if service list provided
        if services:
            service_coverage = self._analyze_service_coverage(alerts, services)
            coverage_analysis['service_coverage_gaps'] = service_coverage
        
        # Identify critical gaps
        critical_gaps = []
        if 'availability' in missing_categories:
            critical_gaps.append("Missing availability monitoring")
        if 'error_rate' in missing_categories:
            critical_gaps.append("Missing error rate monitoring")
        if 'errors' in missing_signals:
            critical_gaps.append("Missing error signal monitoring")
        
        coverage_analysis['critical_gaps'] = critical_gaps
        
        # Generate recommendations
        recommendations = self._generate_coverage_recommendations(coverage_analysis)
        coverage_analysis['recommendations'] = recommendations
        
        return coverage_analysis
