# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402
from debt_dashboard_p0 import HealthMetrics  # noqa: F401,E501


class DebtDashboardMixin3:
    def _calculate_health_metrics(self):
        """Calculate health metrics for each snapshot."""
        self.health_history = []
        
        for snapshot in self.processed_snapshots:
            # Debt density (lower is better)
            debt_density = snapshot["total_debt_items"] / max(1, snapshot["total_files"])
            debt_density_score = max(0, 100 - (debt_density * 20))  # Scale to 0-100
            
            # Complexity score (based on high complexity debt)
            complex_debt_ratio = (snapshot["debt_by_type"].get("high_complexity", 0) + 
                                snapshot["debt_by_type"].get("large_function", 0)) / max(1, snapshot["total_debt_items"])
            complexity_score = max(0, 100 - (complex_debt_ratio * 100))
            
            # Test coverage proxy (based on test debt)
            test_debt_ratio = snapshot["debt_by_category"].get("testing", 0) / max(1, snapshot["total_debt_items"])
            test_coverage_proxy = max(0, 100 - (test_debt_ratio * 150))
            
            # Documentation proxy (based on documentation debt)
            doc_debt_ratio = snapshot["debt_by_category"].get("documentation", 0) / max(1, snapshot["total_debt_items"])
            documentation_proxy = max(0, 100 - (doc_debt_ratio * 100))
            
            # Security score (based on security debt)
            security_debt_ratio = snapshot["security_debt_count"] / max(1, snapshot["total_debt_items"])
            security_score = max(0, 100 - (security_debt_ratio * 200))
            
            # Maintainability (based on architecture and code quality debt)
            maint_debt_count = (snapshot["debt_by_category"].get("architecture", 0) + 
                              snapshot["debt_by_category"].get("code_quality", 0))
            maint_debt_ratio = maint_debt_count / max(1, snapshot["total_debt_items"])
            maintainability = max(0, 100 - (maint_debt_ratio * 120))
            
            # Calculate weighted overall score
            weights = self.health_weights
            overall_score = (
                debt_density_score * weights["debt_density"] +
                complexity_score * weights["complexity_score"] +
                test_coverage_proxy * weights["test_coverage_proxy"] +
                documentation_proxy * weights["documentation_proxy"] +
                security_score * weights["security_score"] +
                maintainability * weights["maintainability"]
            )
            
            # Velocity impact (estimated percentage reduction in team velocity)
            high_impact_ratio = snapshot["high_priority_count"] / max(1, snapshot["total_debt_items"])
            velocity_impact = min(50, high_impact_ratio * 30 + debt_density * 5)
            
            # Technical risk (0-100, higher is more risky)
            risk_factors = snapshot["security_debt_count"] + snapshot["debt_by_type"].get("architecture_debt", 0)
            technical_risk = min(100, risk_factors * 10 + (100 - security_score))
            
            health_metrics = HealthMetrics(
                overall_score=round(overall_score, 1),
                debt_density=round(debt_density, 2),
                velocity_impact=round(velocity_impact, 1),
                quality_score=round((complexity_score + maintainability) / 2, 1),
                maintainability_score=round(maintainability, 1),
                technical_risk_score=round(technical_risk, 1)
            )
            
            # Add timestamp
            health_entry = asdict(health_metrics)
            health_entry["date"] = snapshot["date"]
            self.health_history.append(health_entry)
    def _analyze_trends(self, period: str):
        """Analyze trends in various metrics."""
        self.trend_analyses = {}
        
        if len(self.health_history) < 2:
            return
        
        # Define metrics to analyze
        metrics_to_analyze = [
            "overall_score",
            "debt_density", 
            "velocity_impact",
            "quality_score",
            "technical_risk_score"
        ]
        
        for metric in metrics_to_analyze:
            values = [entry[metric] for entry in self.health_history]
            dates = [datetime.fromisoformat(entry["date"].replace('Z', '+00:00')) 
                    for entry in self.health_history]
            
            trend = self._calculate_trend(values, dates, metric)
            self.trend_analyses[metric] = trend
