# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin5:
    def analyze_thresholds(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze alert thresholds for optimization opportunities."""
        threshold_analysis = []
        
        for alert in alerts:
            alert_name = alert.get('alert', alert.get('name', 'Unknown'))
            expr = alert.get('expr', alert.get('condition', ''))
            
            analysis = {
                'alert_name': alert_name,
                'current_expression': expr,
                'threshold_issues': [],
                'recommendations': []
            }
            
            # Check for hard-coded thresholds
            if re.search(r'[><=]\s*[0-9.]+', expr):
                analysis['threshold_issues'].append('Hard-coded threshold value')
                analysis['recommendations'].append('Consider parameterizing thresholds')
            
            # Check for percentage-based thresholds that might be too strict
            percentage_match = re.search(r'([><=])\s*0?\.\d+', expr)
            if percentage_match:
                operator = percentage_match.group(1)
                if operator in ['>', '>='] and 'error' in expr.lower():
                    analysis['threshold_issues'].append('Very low error rate threshold')
                    analysis['recommendations'].append('Consider increasing error rate threshold based on SLO')
            
            # Check for missing hysteresis
            if '>' in expr and 'for:' not in str(alert):
                analysis['threshold_issues'].append('No hysteresis (for clause)')
                analysis['recommendations'].append('Add "for" clause to prevent alert flapping')
            
            # Check for resource utilization thresholds
            if any(resource in expr.lower() for resource in ['cpu', 'memory', 'disk']):
                threshold_value = self._extract_threshold_from_expression(expr)
                if threshold_value and threshold_value.replace('.', '').isdigit():
                    threshold_num = float(threshold_value)
                    if threshold_num < 0.7:  # Less than 70%
                        analysis['threshold_issues'].append('Low resource utilization threshold')
                        analysis['recommendations'].append('Consider increasing threshold to reduce noise')
            
            # Add historical data analysis if available
            historical_data = alert.get('historical_data', {})
            if historical_data:
                false_positive_rate = historical_data.get('false_positive_rate', 0)
                if false_positive_rate > 0.2:
                    analysis['threshold_issues'].append(f'High false positive rate: {false_positive_rate*100:.1f}%')
                    analysis['recommendations'].append('Analyze historical data and adjust threshold')
            
            if analysis['threshold_issues']:
                threshold_analysis.append(analysis)
        
        return threshold_analysis
