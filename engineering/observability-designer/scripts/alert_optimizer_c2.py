# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin2:
    def _classify_alert_category(self, rule: str, alert_name: str) -> str:
        """Classify alert into monitoring category."""
        rule_lower = rule.lower()
        name_lower = alert_name.lower()
        
        if any(keyword in rule_lower or keyword in name_lower 
               for keyword in ['up', 'down', 'available', 'reachable']):
            return 'availability'
        
        if any(keyword in rule_lower or keyword in name_lower 
               for keyword in ['latency', 'response_time', 'duration']):
            return 'latency'
        
        if any(keyword in rule_lower or keyword in name_lower 
               for keyword in ['error', 'fail', '5xx', '4xx']):
            return 'error_rate'
        
        if any(keyword in rule_lower or keyword in name_lower 
               for keyword in ['cpu', 'memory', 'disk', 'network', 'utilization']):
            return 'resource_utilization'
        
        if any(keyword in rule_lower or keyword in name_lower 
               for keyword in ['security', 'auth', 'login', 'breach']):
            return 'security'
        
        if any(keyword in rule_lower or keyword in name_lower 
               for keyword in ['revenue', 'conversion', 'user', 'business']):
            return 'business_metrics'
        
        return 'other'
    def _identify_golden_signal(self, rule: str) -> str:
        """Identify which golden signal an alert covers."""
        rule_lower = rule.lower()
        
        if any(keyword in rule_lower for keyword in ['latency', 'response_time', 'duration']):
            return 'latency'
        
        if any(keyword in rule_lower for keyword in ['rate', 'rps', 'qps', 'throughput']):
            return 'traffic'
        
        if any(keyword in rule_lower for keyword in ['error', 'fail', '5xx']):
            return 'errors'
        
        if any(keyword in rule_lower for keyword in ['cpu', 'memory', 'disk', 'utilization']):
            return 'saturation'
        
        return None
    def _analyze_service_coverage(self, alerts: List[Dict[str, Any]], 
                                services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze monitoring coverage per service."""
        service_coverage = []
        
        for service in services:
            service_name = service.get('name', '')
            service_alerts = [alert for alert in alerts 
                            if service_name in alert.get('expr', '') or 
                               service_name in alert.get('labels', {}).get('service', '')]
            
            covered_signals = set()
            for alert in service_alerts:
                signal = self._identify_golden_signal(alert.get('expr', ''))
                if signal:
                    covered_signals.add(signal)
            
            missing_signals = set(self.GOLDEN_SIGNALS) - covered_signals
            
            if missing_signals or len(service_alerts) < 3:  # Less than 3 alerts per service
                coverage_gap = {
                    'service': service_name,
                    'alert_count': len(service_alerts),
                    'covered_signals': list(covered_signals),
                    'missing_signals': list(missing_signals),
                    'criticality': service.get('criticality', 'medium'),
                    'recommendations': []
                }
                
                if len(service_alerts) == 0:
                    coverage_gap['recommendations'].append("Add basic availability monitoring")
                if 'errors' in missing_signals:
                    coverage_gap['recommendations'].append("Add error rate monitoring")
                if 'latency' in missing_signals:
                    coverage_gap['recommendations'].append("Add latency monitoring")
                    
                service_coverage.append(coverage_gap)
        
        return service_coverage
