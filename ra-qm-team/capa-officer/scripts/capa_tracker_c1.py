# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from capa_tracker_base import *  # noqa: F403,E402
from capa_tracker_p0 import CAPA, CAPASeverity, CAPASource, CAPAStatus  # noqa: F401,E501


class CAPATrackerMixin1:
    def _generate_recommendations(
        self,
        open_capas: List[CAPA],
        overdue_capas: List[CAPA],
        effectiveness: float,
        avg_cycle: float
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Overdue CAPAs
        if overdue_capas:
            critical_overdue = [c for c in overdue_capas if c.severity == CAPASeverity.CRITICAL]
            if critical_overdue:
                recommendations.append(
                    f"URGENT: {len(critical_overdue)} critical CAPA(s) overdue. "
                    "Escalate to management immediately."
                )
            else:
                recommendations.append(
                    f"ACTION: {len(overdue_capas)} CAPA(s) overdue. "
                    "Review and update target dates or expedite closure."
                )

        # Effectiveness rate
        if effectiveness < 80 and effectiveness > 0:
            recommendations.append(
                f"CONCERN: Effectiveness rate at {effectiveness:.0f}%. "
                "Review root cause analysis quality and corrective action adequacy."
            )

        # Cycle time
        if avg_cycle > 60:
            recommendations.append(
                f"IMPROVEMENT: Average cycle time is {avg_cycle:.0f} days. "
                "Target is 60 days. Review investigation and approval bottlenecks."
            )

        # Investigation backlog
        in_investigation = [c for c in open_capas if c.status == CAPAStatus.INVESTIGATION]
        if len(in_investigation) > 5:
            recommendations.append(
                f"WORKLOAD: {len(in_investigation)} CAPAs in investigation phase. "
                "Consider additional resources or prioritization."
            )

        # Stuck in verification
        in_verification = [c for c in open_capas if c.status == CAPAStatus.VERIFICATION]
        old_verification = [c for c in in_verification if c.days_open > 120]
        if old_verification:
            recommendations.append(
                f"STALLED: {len(old_verification)} CAPA(s) in verification >120 days. "
                "Complete effectiveness checks or extend with justification."
            )

        # Source patterns
        complaint_capas = [c for c in self.capas if c.source == CAPASource.COMPLAINT]
        if len(complaint_capas) > len(self.capas) * 0.4:
            recommendations.append(
                "TREND: >40% of CAPAs from customer complaints. "
                "Review preventive action effectiveness and quality controls."
            )

        if not recommendations:
            recommendations.append(
                "CAPA program operating within targets. "
                "Continue monitoring key metrics."
            )

        return recommendations
    def get_aging_report(self) -> Dict:
        """Generate aging analysis of open CAPAs."""
        open_statuses = [
            CAPAStatus.OPEN, CAPAStatus.INVESTIGATION,
            CAPAStatus.ACTION_PLANNING, CAPAStatus.IMPLEMENTATION,
            CAPAStatus.VERIFICATION
        ]
        open_capas = [c for c in self.capas if c.status in open_statuses]

        aging_buckets = {
            "0-30 days": [],
            "31-60 days": [],
            "61-90 days": [],
            "91-120 days": [],
            ">120 days": []
        }

        for capa in open_capas:
            days = capa.days_open
            if days <= 30:
                bucket = "0-30 days"
            elif days <= 60:
                bucket = "31-60 days"
            elif days <= 90:
                bucket = "61-90 days"
            elif days <= 120:
                bucket = "91-120 days"
            else:
                bucket = ">120 days"

            aging_buckets[bucket].append({
                "capa_number": capa.capa_number,
                "title": capa.title,
                "days_open": days,
                "status": capa.status.value,
                "severity": capa.severity.value
            })

        return aging_buckets
