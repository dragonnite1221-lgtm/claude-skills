# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


class SLODesignerMixin2:
    def calculate_error_budgets(self, slos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate error budgets for SLOs."""
        error_budgets = []
        
        for slo in slos:
            if slo['operator'] == '>=':  # Availability-type SLOs
                target = slo['target_value']
                error_budget_rate = 1 - target
                
                # Calculate budget for different time windows
                time_windows = {
                    '1h': 3600,
                    '1d': 86400,
                    '7d': 604800,
                    '30d': 2592000
                }
                
                budgets = {}
                for window, seconds in time_windows.items():
                    budget_seconds = seconds * error_budget_rate
                    if budget_seconds < 60:
                        budgets[window] = f"{budget_seconds:.1f} seconds"
                    elif budget_seconds < 3600:
                        budgets[window] = f"{budget_seconds/60:.1f} minutes"
                    else:
                        budgets[window] = f"{budget_seconds/3600:.1f} hours"
                
                error_budget = {
                    'slo_name': slo['name'],
                    'error_budget_rate': error_budget_rate,
                    'error_budget_percentage': f"{error_budget_rate * 100:.3f}%",
                    'budgets_by_window': budgets,
                    'burn_rate_alerts': self._generate_burn_rate_alerts(slo, error_budget_rate)
                }
                
                error_budgets.append(error_budget)
                
        return error_budgets
    def _generate_burn_rate_alerts(self, slo: Dict[str, Any], error_budget_rate: float) -> List[Dict[str, Any]]:
        """Generate multi-window burn rate alerts."""
        alerts = []
        service_name = slo['service']
        sli_query = self._get_sli_query_for_burn_rate(slo)
        
        for window_config in self.BURN_RATE_WINDOWS:
            alert = {
                'name': f"{slo['sli_name']} Burn Rate {window_config['budget_consumed']} Alert",
                'description': f"Alert when {slo['sli_name']} is consuming error budget at {window_config['burn_rate']}x rate",
                'severity': self._determine_alert_severity(float(window_config['budget_consumed'].rstrip('%'))),
                'short_window': window_config['short'],
                'long_window': window_config['long'],
                'burn_rate_threshold': window_config['burn_rate'],
                'budget_consumed': window_config['budget_consumed'],
                'condition': f"({sli_query}_short > {window_config['burn_rate']}) and ({sli_query}_long > {window_config['burn_rate']})",
                'annotations': {
                    'summary': f"High burn rate detected for {slo['sli_name']}",
                    'description': f"Error budget consumption rate is {window_config['burn_rate']}x normal, will exhaust {window_config['budget_consumed']} of monthly budget"
                }
            }
            alerts.append(alert)
            
        return alerts
    def _get_sli_query_for_burn_rate(self, slo: Dict[str, Any]) -> str:
        """Generate SLI query fragment for burn rate calculation."""
        service_name = slo['service']
        sli_name = slo['sli_name'].lower().replace(' ', '_')
        
        if 'availability' in sli_name or 'success' in sli_name:
            return f"(1 - (sum(rate(http_requests_total{{service='{service_name}',code!~'5..'}})) / sum(rate(http_requests_total{{service='{service_name}'}}))))"
        elif 'error' in sli_name:
            return f"(sum(rate(http_requests_total{{service='{service_name}',code=~'5..'}})) / sum(rate(http_requests_total{{service='{service_name}'}})))"
        else:
            return f"sli_burn_rate_{sli_name}"
    def _determine_alert_severity(self, budget_consumed_percent: float) -> str:
        """Determine alert severity based on budget consumption rate."""
        if budget_consumed_percent <= 2:
            return 'critical'
        elif budget_consumed_percent <= 5:
            return 'warning'
        else:
            return 'info'
