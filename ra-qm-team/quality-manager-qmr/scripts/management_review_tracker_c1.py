# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from management_review_tracker_base import *  # noqa: F403,E402


class ManagementReviewTrackerMixin1:
    def assess_metrics(self) -> Dict:
        """Assess quality metrics against targets."""
        metrics = self.review.metrics
        assessment = {
            "metrics": [],
            "alerts": [],
            "overall_status": "On Track"
        }

        # Define targets and assess
        checks = [
            ("Complaint Rate", metrics.complaint_rate, 0.1, "lower"),
            ("CAPA Overdue", metrics.capa_overdue, 0, "lower"),
            ("CAPA Effectiveness", metrics.capa_effectiveness, 85.0, "higher"),
            ("First Pass Yield", metrics.first_pass_yield, 95.0, "higher"),
            ("Customer Satisfaction", metrics.customer_satisfaction, 4.0, "higher"),
            ("Training Compliance", metrics.training_compliance, 95.0, "higher"),
        ]

        warnings = 0
        critical = 0

        for name, value, target, direction in checks:
            if direction == "lower":
                status = "Pass" if value <= target else "Fail"
                threshold = target * 1.2
                warning = value > target and value <= threshold
            else:
                status = "Pass" if value >= target else "Fail"
                threshold = target * 0.9
                warning = value < target and value >= threshold

            metric_result = {
                "name": name,
                "value": value,
                "target": target,
                "status": status
            }
            assessment["metrics"].append(metric_result)

            if status == "Fail":
                if warning:
                    warnings += 1
                    assessment["alerts"].append(f"WARNING: {name} at {value} (target: {target})")
                else:
                    critical += 1
                    assessment["alerts"].append(f"CRITICAL: {name} at {value} (target: {target})")

        if critical > 0:
            assessment["overall_status"] = "Critical"
        elif warnings > 0:
            assessment["overall_status"] = "Needs Attention"

        return assessment
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check input readiness
        readiness = self.check_input_readiness()
        if readiness["readiness_score"] < 100:
            recommendations.append(
                f"Complete remaining review inputs: {', '.join(readiness['missing_topics'])}"
            )

        # Check actions
        action_analysis = self.analyze_actions()
        if action_analysis["overdue"]:
            recommendations.append(
                f"Address {len(action_analysis['overdue'])} overdue action(s) immediately"
            )

        # Check metrics
        metrics_assessment = self.assess_metrics()
        if metrics_assessment["overall_status"] == "Critical":
            recommendations.append(
                "Escalate critical metric failures to senior management"
            )

        # CAPA specific
        if self.review.metrics.capa_overdue > 0:
            recommendations.append(
                f"Expedite closure of {self.review.metrics.capa_overdue} overdue CAPA(s)"
            )

        if self.review.metrics.capa_effectiveness < 85:
            recommendations.append(
                "Review root cause analysis quality for ineffective CAPAs"
            )

        # Audit findings
        if self.review.metrics.audit_findings_major > 0:
            recommendations.append(
                f"Prioritize resolution of {self.review.metrics.audit_findings_major} major audit finding(s)"
            )

        if not recommendations:
            recommendations.append("Quality system performing within targets. Maintain monitoring.")

        return recommendations
