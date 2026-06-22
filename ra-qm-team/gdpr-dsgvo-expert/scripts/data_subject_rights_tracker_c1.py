# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_subject_rights_tracker_base import *  # noqa: F403,E402


class RightsTrackerMixin1:
    def list_requests(
        self,
        status_filter: Optional[str] = None,
        overdue_only: bool = False
    ) -> List[Dict]:
        """List requests with optional filtering."""
        results = []
        now = datetime.now()

        for req in self.requests["requests"]:
            if status_filter and req["status"] != status_filter:
                continue

            deadline = datetime.fromisoformat(req["dates"]["deadline"])
            is_overdue = deadline < now and req["status"] not in ["completed", "refused"]

            if overdue_only and not is_overdue:
                continue

            req_summary = {
                **req,
                "is_overdue": is_overdue,
                "days_remaining": (deadline - now).days if not is_overdue else 0
            }
            results.append(req_summary)

        return results
    def generate_report(self) -> Dict:
        """Generate compliance report."""
        now = datetime.now()
        total = len(self.requests["requests"])

        status_counts = {}
        for status in STATUSES:
            status_counts[status] = sum(1 for r in self.requests["requests"] if r["status"] == status)

        type_counts = {}
        for right_type in RIGHTS_TYPES:
            type_counts[right_type] = sum(1 for r in self.requests["requests"] if r["type"] == right_type)

        overdue = []
        completed_on_time = 0
        completed_late = 0

        for req in self.requests["requests"]:
            deadline = datetime.fromisoformat(req["dates"]["deadline"])

            if req["status"] in ["completed", "refused"]:
                completed_date = datetime.fromisoformat(req["dates"]["completed"])
                if completed_date <= deadline:
                    completed_on_time += 1
                else:
                    completed_late += 1
            elif deadline < now:
                overdue.append({
                    "id": req["id"],
                    "type": req["type"],
                    "subject": req["subject"]["name"],
                    "days_overdue": (now - deadline).days
                })

        compliance_rate = (completed_on_time / (completed_on_time + completed_late) * 100) if (completed_on_time + completed_late) > 0 else 100

        return {
            "report_date": now.isoformat(),
            "summary": {
                "total_requests": total,
                "open_requests": total - status_counts.get("completed", 0) - status_counts.get("refused", 0),
                "overdue_requests": len(overdue),
                "compliance_rate": round(compliance_rate, 1)
            },
            "by_status": status_counts,
            "by_type": type_counts,
            "overdue_details": overdue,
            "performance": {
                "completed_on_time": completed_on_time,
                "completed_late": completed_late,
                "average_response_days": self._calculate_avg_response_time()
            }
        }
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time for completed requests."""
        response_times = []

        for req in self.requests["requests"]:
            if req["status"] == "completed" and req["dates"]["completed"]:
                received = datetime.fromisoformat(req["dates"]["received"])
                completed = datetime.fromisoformat(req["dates"]["completed"])
                response_times.append((completed - received).days)

        return round(sum(response_times) / len(response_times), 1) if response_times else 0
