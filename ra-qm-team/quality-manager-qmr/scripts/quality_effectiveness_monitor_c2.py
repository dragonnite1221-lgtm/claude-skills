# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_effectiveness_monitor_base import *  # noqa: F403,E402
from quality_effectiveness_monitor_p0 import QMSReport, QualityMetric  # noqa: F401,E501


class QMSEffectivenessMonitorMixin2:
    def identify_improvement_opportunities(self, metrics: List[QualityMetric]) -> List[Dict]:
        """Identify metrics with highest improvement potential."""
        opportunities = []
        for m in metrics:
            if m.upper_limit and m.value > m.upper_limit * 0.8:
                gap = m.upper_limit - m.value
                if gap > 0:
                    improvement_pct = (gap / m.upper_limit) * 100
                    opportunities.append({
                        "metric": m.metric_name,
                        "current": m.value,
                        "target": m.upper_limit,
                        "gap": round(gap, 2),
                        "improvement_potential_pct": round(improvement_pct, 1),
                        "recommended_action": f"Reduce {m.metric_name} by at least {round(gap, 2)} {m.unit}",
                        "impact": "High" if m.category in ["Customer", "Regulatory"] else "Medium"
                    })

        # Sort by improvement potential
        opportunities.sort(key=lambda x: x["improvement_potential_pct"], reverse=True)
        return opportunities[:10]
    def generate_management_review_summary(self, report: QMSReport) -> str:
        """Generate executive summary for management review."""
        summary = [
            f"QMS EFFECTIVENESS REVIEW - {report.report_period[0]} to {report.report_period[1]}",
            "",
            f"Overall Effectiveness Score: {report.overall_effectiveness_score:.1f}/100",
            f"Metrics Tracked: {report.metrics_count} | In Control: {report.metrics_in_control} | Alerts: {report.critical_alerts}",
            ""
        ]

        if report.critical_alerts > 0:
            summary.append("🔴 CRITICAL ALERTS REQUIRING IMMEDIATE ATTENTION:")
            for alert in [a for a in report.predictive_alerts if a.get("risk_level") == "high"]:
                summary.append(f"  • {alert['metric']}: forecast {alert['forecast_value']} (from {alert['current_value']})")
            summary.append("")

        summary.append("📈 TOP IMPROVEMENT OPPORTUNITIES:")
        for i, opp in enumerate(report.improvement_opportunities[:3], 1):
            summary.append(f"  {i}. {opp['metric']}: {opp['recommended_action']} (Impact: {opp['impact']})")
        summary.append("")

        summary.append("🎯 RECOMMENDED ACTIONS:")
        summary.append("  1. Address all high-severity alerts within 30 days")
        summary.append("  2. Launch improvement projects for top 3 opportunities")
        summary.append("  3. Review CAPA effectiveness for recurring issues")
        summary.append("  4. Update risk assessments based on predictive trends")

        return "\n".join(summary)
    def analyze(
        self,
        metrics: List[QualityMetric],
        start_date: str = None,
        end_date: str = None
    ) -> QMSReport:
        """Perform comprehensive QMS effectiveness analysis."""
        in_control = 0
        for m in metrics:
            if not m.is_alert and not m.is_critical:
                in_control += 1

        out_of_control = len(metrics) - in_control

        alerts = self.detect_alerts(metrics)
        critical_alerts = len([a for a in alerts if a["severity"] in ["critical", "high"]])

        predictions = self.predict_failures(metrics)
        improvement_opps = self.identify_improvement_opportunities(metrics)

        effectiveness = self.calculate_effectiveness_score(metrics)

        # Trend analysis by category
        trends = {}
        categories = set(m.category for m in metrics)
        for cat in categories:
            cat_metrics = [m for m in metrics if m.category == cat]
            if len(cat_metrics) >= 2:
                avg_values = [mean([m.value for m in cat_metrics])]  # Simplistic - would need time series
                trends[cat] = {
                    "metric_count": len(cat_metrics),
                    "avg_value": round(mean([m.value for m in cat_metrics]), 2),
                    "alerts": len([a for a in alerts if any(m.metric_name == a["metric_name"] for m in cat_metrics)])
                }

        period = (start_date or metrics[0].date, end_date or metrics[-1].date) if metrics else ("", "")

        report = QMSReport(
            report_period=period,
            overall_effectiveness_score=effectiveness,
            metrics_count=len(metrics),
            metrics_in_control=in_control,
            metrics_out_of_control=out_of_control,
            critical_alerts=critical_alerts,
            trends_analysis=trends,
            predictive_alerts=predictions,
            improvement_opportunities=improvement_opps,
            management_review_summary=""  # Filled later
        )

        report.management_review_summary = self.generate_management_review_summary(report)

        return report
