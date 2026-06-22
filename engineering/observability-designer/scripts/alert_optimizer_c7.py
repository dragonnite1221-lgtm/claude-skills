# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin7:
    def generate_optimized_config(self, alerts: List[Dict[str, Any]], 
                                analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized alert configuration."""
        optimized_alerts = []
        
        for i, alert in enumerate(alerts):
            optimized_alert = alert.copy()
            alert_name = alert.get('alert', alert.get('name', f'Alert_{i}'))
            
            # Apply noise reduction optimizations
            noisy_alerts = analysis_results.get('noisy_alerts', [])
            for noisy_alert in noisy_alerts:
                if noisy_alert['alert_name'] == alert_name:
                    optimized_alert = self._apply_noise_reduction(optimized_alert, noisy_alert)
                    break
            
            # Apply threshold optimizations
            threshold_issues = analysis_results.get('threshold_analysis', [])
            for threshold_issue in threshold_issues:
                if threshold_issue['alert_name'] == alert_name:
                    optimized_alert = self._apply_threshold_optimization(optimized_alert, threshold_issue)
                    break
            
            # Ensure proper alert metadata
            optimized_alert = self._ensure_alert_metadata(optimized_alert)
            
            optimized_alerts.append(optimized_alert)
        
        # Remove duplicates based on analysis
        if 'duplicate_alerts' in analysis_results:
            optimized_alerts = self._remove_duplicate_alerts(optimized_alerts, 
                                                           analysis_results['duplicate_alerts'])
        
        # Add missing alerts for coverage gaps
        if 'coverage_gaps' in analysis_results:
            new_alerts = self._generate_missing_alerts(analysis_results['coverage_gaps'])
            optimized_alerts.extend(new_alerts)
        
        optimized_config = {
            'alerts': optimized_alerts,
            'optimization_metadata': {
                'optimized_at': datetime.utcnow().isoformat() + 'Z',
                'original_count': len(alerts),
                'optimized_count': len(optimized_alerts),
                'changes_applied': analysis_results.get('optimizations_applied', [])
            }
        }
        
        return optimized_config
    def _apply_noise_reduction(self, alert: Dict[str, Any], 
                             noise_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply noise reduction optimizations to an alert."""
        optimized_alert = alert.copy()
        
        for recommendation in noise_analysis['recommendations']:
            if 'for:' in recommendation and not alert.get('for'):
                optimized_alert['for'] = '5m'
            elif 'threshold' in recommendation.lower():
                # This would require more sophisticated threshold adjustment
                # For now, add annotation for manual review
                if 'annotations' not in optimized_alert:
                    optimized_alert['annotations'] = {}
                optimized_alert['annotations']['optimization_note'] = 'Review threshold - potentially too sensitive'
        
        return optimized_alert
    def _apply_threshold_optimization(self, alert: Dict[str, Any], 
                                    threshold_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply threshold optimizations to an alert."""
        optimized_alert = alert.copy()
        
        # Add 'for' clause if missing
        if 'No hysteresis' in str(threshold_analysis['threshold_issues']):
            if not alert.get('for'):
                optimized_alert['for'] = '5m'
        
        # Add optimization annotations
        if threshold_analysis['recommendations']:
            if 'annotations' not in optimized_alert:
                optimized_alert['annotations'] = {}
            optimized_alert['annotations']['threshold_recommendations'] = '; '.join(threshold_analysis['recommendations'])
        
        return optimized_alert
    def _ensure_alert_metadata(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure alert has proper metadata."""
        optimized_alert = alert.copy()
        
        # Ensure annotations exist
        if 'annotations' not in optimized_alert:
            optimized_alert['annotations'] = {}
        
        # Add summary if missing
        if 'summary' not in optimized_alert['annotations']:
            alert_name = alert.get('alert', alert.get('name', 'Alert'))
            optimized_alert['annotations']['summary'] = f"Alert: {alert_name}"
        
        # Add description if missing
        if 'description' not in optimized_alert['annotations']:
            optimized_alert['annotations']['description'] = 'This alert requires a description. Please update with specific details about the condition and impact.'
        
        # Ensure proper labels
        if 'labels' not in optimized_alert:
            optimized_alert['labels'] = {}
        
        if 'severity' not in optimized_alert['labels']:
            optimized_alert['labels']['severity'] = 'warning'
        
        return optimized_alert
