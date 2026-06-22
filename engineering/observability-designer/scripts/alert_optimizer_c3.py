# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin3:
    def _generate_coverage_recommendations(self, coverage_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations to improve monitoring coverage."""
        recommendations = []
        
        for missing_category in coverage_analysis['missing_categories']:
            if missing_category == 'availability':
                recommendations.append("Add service availability/uptime monitoring")
            elif missing_category == 'latency':
                recommendations.append("Add response time and latency monitoring")
            elif missing_category == 'error_rate':
                recommendations.append("Add error rate and HTTP status code monitoring")
            elif missing_category == 'resource_utilization':
                recommendations.append("Add CPU, memory, and disk utilization monitoring")
            elif missing_category == 'security':
                recommendations.append("Add security monitoring (auth failures, suspicious activity)")
            elif missing_category == 'business_metrics':
                recommendations.append("Add business KPI monitoring")
        
        for missing_signal in coverage_analysis['missing_golden_signals']:
            recommendations.append(f"Implement {missing_signal} monitoring (Golden Signal)")
        
        if coverage_analysis['critical_gaps']:
            recommendations.append("Address critical monitoring gaps as highest priority")
        
        return recommendations
    def find_duplicate_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify duplicate or redundant alerts."""
        duplicates = []
        alert_signatures = defaultdict(list)
        
        # Group alerts by signature
        for i, alert in enumerate(alerts):
            signature = self._generate_alert_signature(alert)
            alert_signatures[signature].append((i, alert))
        
        # Find exact duplicates
        for signature, alert_group in alert_signatures.items():
            if len(alert_group) > 1:
                duplicate_group = {
                    'type': 'exact_duplicate',
                    'signature': signature,
                    'alerts': [{'index': i, 'name': alert.get('alert', alert.get('name', f'Alert_{i}'))} 
                             for i, alert in alert_group],
                    'recommendation': 'Remove duplicate alerts, keep the most comprehensive one'
                }
                duplicates.append(duplicate_group)
        
        # Find semantic duplicates (similar but not identical)
        semantic_duplicates = self._find_semantic_duplicates(alerts)
        duplicates.extend(semantic_duplicates)
        
        return duplicates
    def _generate_alert_signature(self, alert: Dict[str, Any]) -> str:
        """Generate a signature for alert comparison."""
        expr = alert.get('expr', alert.get('condition', ''))
        labels = alert.get('labels', {})
        
        # Normalize the expression by removing whitespace and standardizing
        normalized_expr = re.sub(r'\s+', ' ', expr).strip()
        
        # Create signature from expression and key labels
        key_labels = {k: v for k, v in labels.items() 
                     if k in ['service', 'severity', 'team']}
        
        return f"{normalized_expr}::{json.dumps(key_labels, sort_keys=True)}"
    def _find_semantic_duplicates(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find semantically similar alerts."""
        semantic_duplicates = []
        
        # Group alerts by service and metric type
        service_groups = defaultdict(list)
        
        for i, alert in enumerate(alerts):
            service = self._extract_service_from_alert(alert)
            metric_type = self._extract_metric_type_from_alert(alert)
            key = f"{service}::{metric_type}"
            service_groups[key].append((i, alert))
        
        # Look for similar alerts within each group
        for key, alert_group in service_groups.items():
            if len(alert_group) > 1:
                similar_alerts = self._identify_similar_alerts(alert_group)
                if similar_alerts:
                    semantic_duplicates.extend(similar_alerts)
        
        return semantic_duplicates
    def _extract_service_from_alert(self, alert: Dict[str, Any]) -> str:
        """Extract service name from alert."""
        labels = alert.get('labels', {})
        if 'service' in labels:
            return labels['service']
        
        expr = alert.get('expr', alert.get('condition', ''))
        # Try to extract service from metric labels
        service_match = re.search(r'service="([^"]+)"', expr)
        if service_match:
            return service_match.group(1)
        
        return 'unknown'
