# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402


class IncidentClassifierMixin0:
    """
    Classifies incidents based on description, impact metrics, and business context.
    Provides severity assessment, team recommendations, and response templates.
    """
    def __init__(self):
        """Initialize the classifier with rules and templates."""
        self.severity_rules = self._load_severity_rules()
        self.team_mappings = self._load_team_mappings()
        self.communication_templates = self._load_communication_templates()
        self.action_templates = self._load_action_templates()
    def _load_severity_rules(self) -> Dict[str, Dict]:
        """Load severity classification rules and keywords."""
        return {
            "sev1": {
                "keywords": [
                    "down", "outage", "offline", "unavailable", "crashed", "failed",
                    "critical", "emergency", "dead", "broken", "timeout", "500 error",
                    "data loss", "corrupted", "breach", "security incident",
                    "revenue impact", "customer facing", "all users", "complete failure"
                ],
                "impact_indicators": [
                    "100%", "all users", "entire service", "complete",
                    "revenue loss", "sla violation", "customer churn",
                    "security breach", "data corruption", "regulatory"
                ],
                "duration_threshold": 0,  # Immediate classification
                "response_time": 300,  # 5 minutes
                "description": "Complete service failure affecting all users or critical business functions"
            },
            "sev2": {
                "keywords": [
                    "degraded", "slow", "performance", "errors", "partial",
                    "intermittent", "high latency", "timeouts", "some users",
                    "feature broken", "api errors", "database slow"
                ],
                "impact_indicators": [
                    "50%", "25-75%", "many users", "significant",
                    "performance degradation", "feature unavailable",
                    "support tickets", "user complaints"
                ],
                "duration_threshold": 300,  # 5 minutes
                "response_time": 900,  # 15 minutes
                "description": "Significant degradation affecting subset of users or non-critical functions"
            },
            "sev3": {
                "keywords": [
                    "minor", "cosmetic", "single feature", "workaround available",
                    "edge case", "rare issue", "non-critical", "internal tool",
                    "logging issue", "monitoring gap"
                ],
                "impact_indicators": [
                    "<25%", "few users", "limited impact",
                    "workaround exists", "internal only",
                    "development environment"
                ],
                "duration_threshold": 3600,  # 1 hour
                "response_time": 7200,  # 2 hours
                "description": "Limited impact with workarounds available"
            },
            "sev4": {
                "keywords": [
                    "cosmetic", "documentation", "typo", "minor bug",
                    "enhancement", "nice to have", "low priority",
                    "test environment", "dev tools"
                ],
                "impact_indicators": [
                    "no impact", "cosmetic only", "documentation",
                    "development", "testing", "non-production"
                ],
                "duration_threshold": 86400,  # 24 hours
                "response_time": 172800,  # 2 days
                "description": "Minimal impact, cosmetic issues, or planned maintenance"
            }
        }
    def _load_team_mappings(self) -> Dict[str, List[str]]:
        """Load team assignment rules based on service/component keywords."""
        return {
            "database": ["Database Team", "SRE", "Backend Engineering"],
            "frontend": ["Frontend Team", "UX Engineering", "Product Engineering"],
            "api": ["API Team", "Backend Engineering", "Platform Team"],
            "infrastructure": ["SRE", "DevOps", "Platform Team"],
            "security": ["Security Team", "SRE", "Compliance Team"],
            "network": ["Network Engineering", "SRE", "Infrastructure Team"],
            "authentication": ["Identity Team", "Security Team", "Backend Engineering"],
            "payment": ["Payments Team", "Finance Engineering", "Compliance Team"],
            "mobile": ["Mobile Team", "API Team", "QA Engineering"],
            "monitoring": ["SRE", "Platform Team", "DevOps"],
            "deployment": ["DevOps", "Release Engineering", "SRE"],
            "data": ["Data Engineering", "Analytics Team", "Backend Engineering"]
        }
