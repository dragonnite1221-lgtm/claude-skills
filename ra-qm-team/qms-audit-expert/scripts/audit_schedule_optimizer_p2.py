# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_schedule_optimizer_base import *  # noqa: F403,E402
# fmt: off
from audit_schedule_optimizer_p1 import AuditFrequency, AuditSchedule, AuditSlot, Process, RiskLevel  # noqa: E402,E501
# fmt: on


class AuditScheduleOptimizer:
    """Optimizer for risk-based audit scheduling."""

    # Frequency mapping by risk level
    FREQUENCY_MAP = {
        RiskLevel.HIGH: AuditFrequency.QUARTERLY,
        RiskLevel.MEDIUM: AuditFrequency.SEMI_ANNUAL,
        RiskLevel.LOW: AuditFrequency.ANNUAL,
    }

    # ISO 13485 required processes
    REQUIRED_PROCESSES = [
        ("Document Control", "4.2"),
        ("Management Review", "5.6"),
        ("Training and Competency", "6.2"),
        ("Design Control", "7.3"),
        ("Purchasing", "7.4"),
        ("Production Control", "7.5"),
        ("Equipment Calibration", "7.6"),
        ("Customer Feedback", "8.2.1"),
        ("Internal Audit", "8.2.2"),
        ("Nonconforming Product", "8.3"),
        ("CAPA", "8.5"),
    ]

    def __init__(self, processes: List[Process], audit_days_per_month: int = 4):
        self.processes = processes
        self.audit_days_per_month = audit_days_per_month
        self.today = datetime.now()

    def calculate_priority_score(self, process: Process) -> float:
        """Calculate audit priority score based on multiple factors."""
        score = 0.0

        # Base risk score (40% weight)
        risk_scores = {RiskLevel.HIGH: 10, RiskLevel.MEDIUM: 6, RiskLevel.LOW: 3}
        score += risk_scores[process.risk_level] * 0.4

        # Overdue factor (30% weight)
        if process.last_audit_date:
            last_audit = datetime.strptime(process.last_audit_date, "%Y-%m-%d")
            days_since = (self.today - last_audit).days
            required_frequency = self.FREQUENCY_MAP[process.risk_level].value
            overdue_ratio = days_since / required_frequency
            score += min(overdue_ratio * 10, 10) * 0.3
        else:
            # Never audited = highest priority
            score += 10 * 0.3

        # Previous findings factor (20% weight)
        findings_score = min(process.previous_findings * 2, 10)
        score += findings_score * 0.2

        # Criticality factor (10% weight)
        score += process.criticality_score * 0.1

        return round(score, 2)

    def get_days_overdue(self, process: Process) -> int:
        """Calculate days overdue for audit."""
        if not process.last_audit_date:
            return 365  # Assume 1 year overdue if never audited

        last_audit = datetime.strptime(process.last_audit_date, "%Y-%m-%d")
        required_frequency = self.FREQUENCY_MAP[process.risk_level].value
        next_due = last_audit + timedelta(days=required_frequency)
        days_overdue = (self.today - next_due).days

        return max(0, days_overdue)

    def generate_schedule(self, months_ahead: int = 12) -> AuditSchedule:
        """Generate optimized audit schedule."""
        # Calculate priority scores
        prioritized = []
        for process in self.processes:
            priority = self.calculate_priority_score(process)
            overdue = self.get_days_overdue(process)
            prioritized.append((process, priority, overdue))

        # Sort by priority (descending)
        prioritized.sort(key=lambda x: x[1], reverse=True)

        # Generate schedule slots
        schedule = []
        current_date = self.today
        audits_per_quarter = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

        for process, priority, overdue in prioritized:
            # Determine schedule date based on priority
            if overdue > 0:
                # Overdue: schedule within next 30 days
                scheduled_date = current_date + timedelta(days=min(30, overdue // 10 + 7))
            elif priority > 7:
                # High priority: within 60 days
                scheduled_date = current_date + timedelta(days=30)
            elif priority > 4:
                # Medium priority: within 120 days
                scheduled_date = current_date + timedelta(days=90)
            else:
                # Low priority: within 180 days
                scheduled_date = current_date + timedelta(days=180)

            # Cap at months_ahead
            max_date = current_date + timedelta(days=months_ahead * 30)
            if scheduled_date > max_date:
                scheduled_date = max_date

            # Track quarter distribution
            quarter = f"Q{(scheduled_date.month - 1) // 3 + 1}"
            audits_per_quarter[quarter] += 1

            # Generate rationale
            rationale_parts = []
            if overdue > 0:
                rationale_parts.append(f"{overdue} days overdue")
            if process.previous_findings > 0:
                rationale_parts.append(f"{process.previous_findings} previous findings")
            if process.risk_level == RiskLevel.HIGH:
                rationale_parts.append("high-risk process")
            rationale = "; ".join(rationale_parts) if rationale_parts else "Scheduled per frequency"

            slot = AuditSlot(
                process_name=process.name,
                iso_clause=process.iso_clause,
                scheduled_date=scheduled_date.strftime("%Y-%m-%d"),
                risk_level=process.risk_level.value,
                priority_score=priority,
                days_overdue=overdue,
                rationale=rationale
            )
            schedule.append(slot)

        # Generate recommendations
        recommendations = self._generate_recommendations(prioritized)

        return AuditSchedule(
            generated_date=self.today.strftime("%Y-%m-%d"),
            schedule_period=f"{self.today.strftime('%Y-%m-%d')} to {(self.today + timedelta(days=months_ahead * 30)).strftime('%Y-%m-%d')}",
            total_audits=len(schedule),
            audits_by_quarter=audits_per_quarter,
            schedule=[asdict(s) for s in schedule],
            recommendations=recommendations
        )

    def _generate_recommendations(self, prioritized: List) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check for overdue audits
        overdue_count = sum(1 for _, _, overdue in prioritized if overdue > 0)
        if overdue_count > 0:
            recommendations.append(
                f"URGENT: {overdue_count} process(es) overdue for audit. "
                "Prioritize these to maintain compliance."
            )

        # Check for high-risk processes
        high_risk_count = sum(1 for p, _, _ in prioritized if p.risk_level == RiskLevel.HIGH)
        if high_risk_count > 3:
            recommendations.append(
                f"High audit burden: {high_risk_count} high-risk processes. "
                "Consider quarterly resource allocation."
            )

        # Check for processes with multiple findings
        finding_processes = [(p.name, p.previous_findings) for p, _, _ in prioritized if p.previous_findings >= 3]
        if finding_processes:
            names = ", ".join([name for name, _ in finding_processes[:3]])
            recommendations.append(
                f"Recurring issues in: {names}. "
                "Consider focused audits or process improvement initiatives."
            )

        # Check for never-audited processes
        never_audited = [p.name for p, _, _ in prioritized if not p.last_audit_date]
        if never_audited:
            recommendations.append(
                f"Never audited: {', '.join(never_audited[:3])}. "
                "Include in next audit cycle."
            )

        if not recommendations:
            recommendations.append("Audit program is on track. Maintain scheduled frequency.")

        return recommendations
