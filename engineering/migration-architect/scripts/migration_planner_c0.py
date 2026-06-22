# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import RiskItem  # noqa: F401,E501


class MigrationPlannerMixin0:
    """Main migration planner class"""
    def __init__(self):
        self.migration_patterns = self._load_migration_patterns()
        self.risk_templates = self._load_risk_templates()
    def _load_migration_patterns(self) -> Dict[str, Any]:
        """Load predefined migration patterns"""
        return {
            "database": {
                "schema_change": {
                    "phases": ["preparation", "expand", "migrate", "contract", "cleanup"],
                    "base_duration": 24,
                    "complexity_multiplier": {"low": 1.0, "medium": 1.5, "high": 2.5, "critical": 4.0}
                },
                "data_migration": {
                    "phases": ["assessment", "setup", "bulk_copy", "delta_sync", "validation", "cutover"],
                    "base_duration": 48,
                    "complexity_multiplier": {"low": 1.2, "medium": 2.0, "high": 3.0, "critical": 5.0}
                }
            },
            "service": {
                "strangler_fig": {
                    "phases": ["intercept", "implement", "redirect", "validate", "retire"],
                    "base_duration": 168,  # 1 week
                    "complexity_multiplier": {"low": 0.8, "medium": 1.0, "high": 1.8, "critical": 3.0}
                },
                "parallel_run": {
                    "phases": ["setup", "deploy", "shadow", "compare", "cutover", "cleanup"],
                    "base_duration": 72,
                    "complexity_multiplier": {"low": 1.0, "medium": 1.3, "high": 2.0, "critical": 3.5}
                }
            },
            "infrastructure": {
                "cloud_migration": {
                    "phases": ["assessment", "design", "pilot", "migration", "optimization", "decommission"],
                    "base_duration": 720,  # 30 days
                    "complexity_multiplier": {"low": 0.6, "medium": 1.0, "high": 1.5, "critical": 2.5}
                },
                "on_prem_to_cloud": {
                    "phases": ["discovery", "planning", "pilot", "migration", "validation", "cutover"],
                    "base_duration": 480,  # 20 days
                    "complexity_multiplier": {"low": 0.8, "medium": 1.2, "high": 2.0, "critical": 3.0}
                }
            }
        }
    def _load_risk_templates(self) -> Dict[str, List[RiskItem]]:
        """Load risk templates for different migration types"""
        return {
            "database": [
                RiskItem("technical", "Data corruption during migration", "low", "critical", "high",
                        "Implement comprehensive backup and validation procedures", "DBA Team"),
                RiskItem("technical", "Extended downtime due to migration complexity", "medium", "high", "high",
                        "Use blue-green deployment and phased migration approach", "DevOps Team"),
                RiskItem("business", "Business process disruption", "medium", "high", "high",
                        "Communicate timeline and provide alternate workflows", "Business Owner"),
                RiskItem("operational", "Insufficient rollback testing", "high", "critical", "critical",
                        "Execute full rollback procedures in staging environment", "QA Team")
            ],
            "service": [
                RiskItem("technical", "Service compatibility issues", "medium", "high", "high",
                        "Implement comprehensive integration testing", "Development Team"),
                RiskItem("technical", "Performance degradation", "medium", "medium", "medium",
                        "Conduct load testing and performance benchmarking", "DevOps Team"),
                RiskItem("business", "Feature parity gaps", "high", "high", "high",
                        "Document feature mapping and acceptance criteria", "Product Owner"),
                RiskItem("operational", "Monitoring gap during transition", "medium", "medium", "medium",
                        "Set up dual monitoring and alerting systems", "SRE Team")
            ],
            "infrastructure": [
                RiskItem("technical", "Network connectivity issues", "medium", "critical", "high",
                        "Implement redundant network paths and monitoring", "Network Team"),
                RiskItem("technical", "Security configuration drift", "high", "high", "high",
                        "Automated security scanning and compliance checks", "Security Team"),
                RiskItem("business", "Cost overrun during transition", "high", "medium", "medium",
                        "Implement cost monitoring and budget alerts", "Finance Team"),
                RiskItem("operational", "Team knowledge gaps", "high", "medium", "medium",
                        "Provide training and create detailed documentation", "Platform Team")
            ]
        }
