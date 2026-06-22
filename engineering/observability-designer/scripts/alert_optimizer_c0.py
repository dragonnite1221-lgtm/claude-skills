# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin0:
    """Analyze and optimize alert configurations."""
    SEVERITY_PRIORITY = {
        'critical': 1,
        'high': 2,
        'warning': 3,
        'info': 4
    }
    NOISY_PATTERNS = [
        r'disk.*usage.*>.*[89]\d%',  # Disk usage > 80% often noisy
        r'memory.*>.*[89]\d%',       # Memory > 80% often noisy
        r'cpu.*>.*[789]\d%',         # CPU > 70% can be noisy
        r'response.*time.*>.*\d+ms', # Low latency thresholds
        r'error.*rate.*>.*0\.[01]%'  # Very low error rate thresholds
    ]
    COVERAGE_CATEGORIES = [
        'availability',
        'latency', 
        'error_rate',
        'resource_utilization',
        'security',
        'business_metrics'
    ]
    GOLDEN_SIGNALS = [
        'latency',
        'traffic',
        'errors', 
        'saturation'
    ]
    def __init__(self):
        """Initialize the Alert Optimizer."""
        self.alert_config = {}
        self.optimization_results = {}
        self.alert_analysis = {}
    def load_alert_config(self, file_path: str) -> Dict[str, Any]:
        """Load alert configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Alert configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in alert configuration: {e}")
    def analyze_alert_noise(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potentially noisy alerts."""
        noisy_alerts = []
        
        for alert in alerts:
            noise_score = 0
            noise_reasons = []
            
            alert_rule = alert.get('expr', alert.get('condition', ''))
            alert_name = alert.get('alert', alert.get('name', 'Unknown'))
            
            # Check for common noisy patterns
            for pattern in self.NOISY_PATTERNS:
                if re.search(pattern, alert_rule, re.IGNORECASE):
                    noise_score += 3
                    noise_reasons.append(f"Matches noisy pattern: {pattern}")
            
            # Check for very frequent evaluation intervals
            evaluation_interval = alert.get('for', '0s')
            if self._parse_duration(evaluation_interval) < 60:  # Less than 1 minute
                noise_score += 2
                noise_reasons.append("Very short evaluation interval")
            
            # Check for lack of 'for' clause
            if not alert.get('for') or alert.get('for') == '0s':
                noise_score += 2
                noise_reasons.append("No 'for' clause - may cause alert flapping")
            
            # Check for overly sensitive thresholds
            if self._has_sensitive_threshold(alert_rule):
                noise_score += 2
                noise_reasons.append("Potentially sensitive threshold")
            
            # Check historical firing rate if available
            historical_data = alert.get('historical_data', {})
            if historical_data:
                firing_rate = historical_data.get('fires_per_day', 0)
                if firing_rate > 10:  # More than 10 fires per day
                    noise_score += 3
                    noise_reasons.append(f"High firing rate: {firing_rate} times/day")
                
                false_positive_rate = historical_data.get('false_positive_rate', 0)
                if false_positive_rate > 0.3:  # > 30% false positives
                    noise_score += 4
                    noise_reasons.append(f"High false positive rate: {false_positive_rate*100:.1f}%")
            
            if noise_score >= 3:  # Threshold for considering an alert noisy
                noisy_alert = {
                    'alert_name': alert_name,
                    'noise_score': noise_score,
                    'reasons': noise_reasons,
                    'current_rule': alert_rule,
                    'recommendations': self._generate_noise_reduction_recommendations(alert, noise_reasons)
                }
                noisy_alerts.append(noisy_alert)
        
        return sorted(noisy_alerts, key=lambda x: x['noise_score'], reverse=True)
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds."""
        if not duration_str or duration_str == '0s':
            return 0
        
        duration_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        match = re.match(r'(\d+)([smhd])', duration_str)
        if match:
            value, unit = match.groups()
            return int(value) * duration_map.get(unit, 1)
        return 0
    def _has_sensitive_threshold(self, rule: str) -> bool:
        """Check if alert rule has potentially sensitive thresholds."""
        # Look for very low error rates or very tight latency thresholds
        sensitive_patterns = [
            r'error.*rate.*>.*0\.0[01]',     # Error rate > 0.01% or 0.001%
            r'latency.*>.*[12]\d\d?ms',      # Latency > 100-299ms
            r'response.*time.*>.*0\.[12]',   # Response time > 0.1-0.2s
            r'cpu.*>.*[456]\d%'              # CPU > 40-69% (too sensitive for most cases)
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, rule, re.IGNORECASE):
                return True
        return False
