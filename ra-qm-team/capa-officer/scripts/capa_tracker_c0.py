# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from capa_tracker_base import *  # noqa: F403,E402
from capa_tracker_p0 import CAPA, CAPAMetrics, CAPASeverity, CAPASource, CAPAStatus  # noqa: F401,E501


class CAPATrackerMixin0:
    """CAPA tracking and metrics calculator."""
    TARGET_CYCLE_TIMES = {
        CAPASeverity.CRITICAL: 30,
        CAPASeverity.MAJOR: 60,
        CAPASeverity.MINOR: 90,
    }
    def __init__(self, capas: List[CAPA]):
        self.capas = capas
        self.today = datetime.now()
        self._calculate_derived_fields()
    def _calculate_derived_fields(self):
        """Calculate days open and overdue status."""
        for capa in self.capas:
            open_date = datetime.strptime(capa.open_date, "%Y-%m-%d")

            if capa.close_date:
                close_date = datetime.strptime(capa.close_date, "%Y-%m-%d")
                capa.days_open = (close_date - open_date).days
            else:
                capa.days_open = (self.today - open_date).days

            target_date = datetime.strptime(capa.target_date, "%Y-%m-%d")
            if not capa.close_date and self.today > target_date:
                capa.is_overdue = True
    def calculate_metrics(self) -> CAPAMetrics:
        """Calculate comprehensive CAPA metrics."""
        total = len(self.capas)

        # Status counts
        closed_statuses = [CAPAStatus.CLOSED_EFFECTIVE, CAPAStatus.CLOSED_INEFFECTIVE]
        open_capas = [c for c in self.capas if c.status not in closed_statuses]
        closed_capas = [c for c in self.capas if c.status in closed_statuses]
        overdue_capas = [c for c in self.capas if c.is_overdue]

        # Average cycle time (closed CAPAs only)
        if closed_capas:
            avg_cycle = sum(c.days_open for c in closed_capas) / len(closed_capas)
        else:
            avg_cycle = 0.0

        # Effectiveness rate
        effective = [c for c in self.capas if c.status == CAPAStatus.CLOSED_EFFECTIVE]
        ineffective = [c for c in self.capas if c.status == CAPAStatus.CLOSED_INEFFECTIVE]
        if effective or ineffective:
            effectiveness = len(effective) / (len(effective) + len(ineffective)) * 100
        else:
            effectiveness = 0.0

        # Counts by category
        by_status = {}
        for status in CAPAStatus:
            count = len([c for c in self.capas if c.status == status])
            if count > 0:
                by_status[status.value] = count

        by_severity = {}
        for severity in CAPASeverity:
            count = len([c for c in self.capas if c.severity == severity])
            if count > 0:
                by_severity[severity.value] = count

        by_source = {}
        for source in CAPASource:
            count = len([c for c in self.capas if c.source == source])
            if count > 0:
                by_source[source.value] = count

        # Overdue list
        overdue_list = []
        for capa in sorted(overdue_capas, key=lambda c: c.days_open, reverse=True):
            target = datetime.strptime(capa.target_date, "%Y-%m-%d")
            days_overdue = (self.today - target).days
            overdue_list.append({
                "capa_number": capa.capa_number,
                "title": capa.title,
                "severity": capa.severity.value,
                "status": capa.status.value,
                "days_overdue": days_overdue,
                "owner": capa.owner
            })

        # Generate recommendations
        recommendations = self._generate_recommendations(
            open_capas, overdue_capas, effectiveness, avg_cycle
        )

        return CAPAMetrics(
            total_capas=total,
            open_capas=len(open_capas),
            closed_capas=len(closed_capas),
            overdue_capas=len(overdue_capas),
            avg_cycle_time=round(avg_cycle, 1),
            effectiveness_rate=round(effectiveness, 1),
            by_status=by_status,
            by_severity=by_severity,
            by_source=by_source,
            overdue_list=overdue_list,
            recommendations=recommendations
        )
