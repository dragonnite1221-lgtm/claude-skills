# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_subject_rights_tracker_base import *  # noqa: F403,E402


class RightsTrackerMixin0:
    """Manages data subject rights requests."""
    def __init__(self, data_file: str = "dsr_requests.json"):
        self.data_file = Path(data_file)
        self.requests = self._load_requests()
    def _load_requests(self) -> Dict:
        """Load requests from file."""
        if self.data_file.exists():
            with open(self.data_file, "r") as f:
                return json.load(f)
        return {"requests": [], "metadata": {"created": datetime.now().isoformat()}}
    def _save_requests(self):
        """Save requests to file."""
        self.requests["metadata"]["updated"] = datetime.now().isoformat()
        with open(self.data_file, "w") as f:
            json.dump(self.requests, f, indent=2)
    def _generate_id(self) -> str:
        """Generate unique request ID."""
        count = len(self.requests["requests"]) + 1
        return f"DSR-{datetime.now().strftime('%Y%m')}-{count:04d}"
    def add_request(
        self,
        right_type: str,
        subject_name: str,
        subject_email: str,
        details: str = ""
    ) -> Dict:
        """Add a new data subject request."""
        if right_type not in RIGHTS_TYPES:
            raise ValueError(f"Invalid right type. Must be one of: {list(RIGHTS_TYPES.keys())}")

        right_info = RIGHTS_TYPES[right_type]
        now = datetime.now()
        deadline = now + timedelta(days=right_info["deadline_days"])

        request = {
            "id": self._generate_id(),
            "type": right_type,
            "article": right_info["article"],
            "right_name": right_info["name"],
            "subject": {
                "name": subject_name,
                "email": subject_email,
                "verified": False
            },
            "details": details,
            "status": "received",
            "status_description": STATUSES["received"],
            "dates": {
                "received": now.isoformat(),
                "deadline": deadline.isoformat(),
                "verified": None,
                "completed": None
            },
            "notes": [],
            "response": None
        }

        self.requests["requests"].append(request)
        self._save_requests()
        return request
    def update_status(
        self,
        request_id: str,
        new_status: str,
        note: str = ""
    ) -> Optional[Dict]:
        """Update request status."""
        if new_status not in STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {list(STATUSES.keys())}")

        for req in self.requests["requests"]:
            if req["id"] == request_id:
                req["status"] = new_status
                req["status_description"] = STATUSES[new_status]

                if new_status == "verified":
                    req["subject"]["verified"] = True
                    req["dates"]["verified"] = datetime.now().isoformat()
                elif new_status == "completed":
                    req["dates"]["completed"] = datetime.now().isoformat()
                elif new_status == "extended":
                    # Extend deadline by additional 60 days (max total 90)
                    original_deadline = datetime.fromisoformat(req["dates"]["deadline"])
                    req["dates"]["deadline"] = (original_deadline + timedelta(days=60)).isoformat()

                if note:
                    req["notes"].append({
                        "timestamp": datetime.now().isoformat(),
                        "note": note
                    })

                self._save_requests()
                return req

        return None
    def get_request(self, request_id: str) -> Optional[Dict]:
        """Get request by ID."""
        for req in self.requests["requests"]:
            if req["id"] == request_id:
                return req
        return None
