# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin4:
    def _extract_metric_type_from_alert(self, alert: Dict[str, Any]) -> str:
        """Extract metric type from alert."""
        expr = alert.get('expr', alert.get('condition', ''))
        
        # Common metric patterns
        if 'up' in expr.lower():
            return 'availability'
        elif any(keyword in expr.lower() for keyword in ['latency', 'duration', 'response_time']):
            return 'latency'
        elif any(keyword in expr.lower() for keyword in ['error', 'fail', '5xx']):
            return 'error_rate'
        elif any(keyword in expr.lower() for keyword in ['cpu', 'memory', 'disk']):
            return 'resource'
        
        return 'other'
    def _identify_similar_alerts(self, alert_group: List[Tuple[int, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify similar alerts within a group."""
        similar_groups = []
        
        # Simple similarity check based on threshold values and conditions
        threshold_groups = defaultdict(list)
        
        for index, alert in alert_group:
            expr = alert.get('expr', alert.get('condition', ''))
            threshold = self._extract_threshold_from_expression(expr)
            severity = alert.get('labels', {}).get('severity', 'unknown')
            
            similarity_key = f"{threshold}::{severity}"
            threshold_groups[similarity_key].append((index, alert))
        
        # If multiple alerts have very similar thresholds, they might be redundant
        for similarity_key, similar_alerts in threshold_groups.items():
            if len(similar_alerts) > 1:
                similar_group = {
                    'type': 'semantic_duplicate',
                    'similarity_key': similarity_key,
                    'alerts': [{'index': i, 'name': alert.get('alert', alert.get('name', f'Alert_{i}'))} 
                             for i, alert in similar_alerts],
                    'recommendation': 'Review for potential consolidation - similar thresholds and conditions'
                }
                similar_groups.append(similar_group)
        
        return similar_groups
    def _extract_threshold_from_expression(self, expr: str) -> str:
        """Extract threshold value from alert expression."""
        # Look for common threshold patterns
        threshold_patterns = [
            r'>[\s]*([0-9.]+)',
            r'<[\s]*([0-9.]+)',
            r'>=[\s]*([0-9.]+)',
            r'<=[\s]*([0-9.]+)',
            r'==[\s]*([0-9.]+)'
        ]
        
        for pattern in threshold_patterns:
            match = re.search(pattern, expr)
            if match:
                return match.group(1)
        
        return 'unknown'
