# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fmea_analyzer_base import *  # noqa: F403,E402
# fmt: off
from fmea_analyzer_p1 import FMEAEntry, FMEAReport, FMEAType  # noqa: E402,E501
# fmt: on


class FMEAAnalyzer:
    """Analyzes FMEA data and generates risk assessments."""

    # RPN thresholds
    RPN_CRITICAL = 200
    RPN_HIGH = 100
    RPN_MEDIUM = 50

    def __init__(self, fmea_type: FMEAType = FMEAType.DESIGN):
        self.fmea_type = fmea_type

    def analyze_entries(self, entries: List[FMEAEntry]) -> Dict:
        """Analyze all FMEA entries and generate summary."""
        for entry in entries:
            entry.calculate_rpn()
            entry.calculate_revised_rpn()

        rpns = [e.rpn for e in entries if e.rpn > 0]
        revised_rpns = [e.revised_rpn for e in entries if e.revised_rpn > 0]

        critical = [e for e in entries if e.criticality == "CRITICAL"]
        high = [e for e in entries if e.criticality == "HIGH"]
        medium = [e for e in entries if e.criticality == "MEDIUM"]

        # Severity distribution
        sev_dist = {}
        for e in entries:
            sev_range = "1-3 (Low)" if e.severity <= 3 else "4-6 (Medium)" if e.severity <= 6 else "7-10 (High)"
            sev_dist[sev_range] = sev_dist.get(sev_range, 0) + 1

        summary = {
            "total_entries": len(entries),
            "rpn_statistics": {
                "min": min(rpns) if rpns else 0,
                "max": max(rpns) if rpns else 0,
                "average": round(sum(rpns) / len(rpns), 1) if rpns else 0,
                "median": sorted(rpns)[len(rpns) // 2] if rpns else 0
            },
            "risk_distribution": {
                "critical_severity": len(critical),
                "high_rpn": len(high),
                "medium_rpn": len(medium),
                "low_rpn": len(entries) - len(critical) - len(high) - len(medium)
            },
            "severity_distribution": sev_dist,
            "top_risks": [
                {
                    "item": e.item_process,
                    "failure_mode": e.failure_mode,
                    "rpn": e.rpn,
                    "severity": e.severity
                }
                for e in sorted(entries, key=lambda x: x.rpn, reverse=True)[:5]
            ]
        }

        if revised_rpns:
            summary["revised_rpn_statistics"] = {
                "min": min(revised_rpns),
                "max": max(revised_rpns),
                "average": round(sum(revised_rpns) / len(revised_rpns), 1),
                "improvement": round((sum(rpns) - sum(revised_rpns)) / sum(rpns) * 100, 1) if rpns else 0
            }

        return summary

    def generate_risk_reduction_actions(self, entries: List[FMEAEntry]) -> List[Dict]:
        """Generate recommended risk reduction actions."""
        actions = []

        # Sort by RPN descending
        sorted_entries = sorted(entries, key=lambda e: e.rpn, reverse=True)

        for entry in sorted_entries[:10]:  # Top 10 risks
            if entry.rpn >= self.RPN_HIGH or entry.severity >= 8:
                strategies = []

                # Severity reduction strategies (highest priority for high severity)
                if entry.severity >= 7:
                    strategies.append({
                        "type": "Severity Reduction",
                        "action": f"Redesign {entry.item_process} to eliminate failure mode: {entry.failure_mode}",
                        "priority": "Highest",
                        "expected_impact": "May reduce severity by 2-4 points"
                    })

                # Occurrence reduction strategies
                if entry.occurrence >= 5:
                    strategies.append({
                        "type": "Occurrence Reduction",
                        "action": f"Implement preventive controls for cause: {entry.cause}",
                        "priority": "High",
                        "expected_impact": f"Target occurrence reduction from {entry.occurrence} to {max(1, entry.occurrence - 3)}"
                    })

                # Detection improvement strategies
                if entry.detection >= 5:
                    strategies.append({
                        "type": "Detection Improvement",
                        "action": f"Enhance detection methods: {entry.current_controls}",
                        "priority": "Medium",
                        "expected_impact": f"Target detection improvement from {entry.detection} to {max(1, entry.detection - 3)}"
                    })

                actions.append({
                    "item": entry.item_process,
                    "failure_mode": entry.failure_mode,
                    "current_rpn": entry.rpn,
                    "current_severity": entry.severity,
                    "strategies": strategies
                })

        return actions

    def create_entry_from_dict(self, data: Dict) -> FMEAEntry:
        """Create FMEA entry from dictionary."""
        entry = FMEAEntry(
            item_process=data.get("item_process", ""),
            function=data.get("function", ""),
            failure_mode=data.get("failure_mode", ""),
            effect=data.get("effect", ""),
            severity=data.get("severity", 1),
            cause=data.get("cause", ""),
            occurrence=data.get("occurrence", 1),
            current_controls=data.get("current_controls", ""),
            detection=data.get("detection", 1),
            recommended_actions=data.get("recommended_actions", []),
            responsibility=data.get("responsibility", ""),
            target_date=data.get("target_date", ""),
            actions_taken=data.get("actions_taken", ""),
            revised_severity=data.get("revised_severity", 0),
            revised_occurrence=data.get("revised_occurrence", 0),
            revised_detection=data.get("revised_detection", 0)
        )
        entry.calculate_rpn()
        entry.calculate_revised_rpn()
        return entry

    def generate_report(self, product_process: str, team: List[str], entries_data: List[Dict]) -> FMEAReport:
        """Generate complete FMEA report."""
        entries = [self.create_entry_from_dict(e) for e in entries_data]
        summary = self.analyze_entries(entries)
        actions = self.generate_risk_reduction_actions(entries)

        return FMEAReport(
            fmea_type=self.fmea_type.value,
            product_process=product_process,
            team=team,
            date=datetime.now().strftime("%Y-%m-%d"),
            entries=entries,
            summary=summary,
            risk_reduction_actions=actions
        )
