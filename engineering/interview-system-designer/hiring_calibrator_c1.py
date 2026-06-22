# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin1:
    def _validate_interview_record(self, record: Dict[str, Any]) -> bool:
        """Validate that an interview record has required fields."""
        required_fields = ["candidate_id", "interviewer_id", "scores", "overall_recommendation", "date"]
        
        for field in required_fields:
            if field not in record or record[field] is None:
                return False
        
        # Validate scores format
        if not isinstance(record["scores"], dict):
            return False
        
        # Validate score values are numeric and in valid range (1-4)
        for competency, score in record["scores"].items():
            if not isinstance(score, (int, float)) or not (1 <= score <= 4):
                return False
        
        return True
    def _standardize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize record format and add computed fields."""
        standardized = record.copy()
        
        # Calculate average score
        scores = list(record["scores"].values())
        standardized["average_score"] = statistics.mean(scores)
        
        # Standardize recommendation to binary
        recommendation = record["overall_recommendation"].lower()
        standardized["hire_decision"] = recommendation in ["hire", "strong hire", "yes"]
        
        # Parse date if string
        if isinstance(record["date"], str):
            try:
                standardized["date"] = datetime.fromisoformat(record["date"].replace("Z", "+00:00"))
            except ValueError:
                standardized["date"] = datetime.now()
        
        # Add demographic info if available
        for category in self.demographic_categories:
            if category not in standardized:
                standardized[category] = "unknown"
        
        # Add level normalization
        role = record.get("role", "").lower()
        if any(level in role for level in ["junior", "associate", "entry"]):
            standardized["normalized_level"] = "junior"
        elif any(level in role for level in ["senior", "sr"]):
            standardized["normalized_level"] = "senior"  
        elif any(level in role for level in ["staff", "principal", "lead"]):
            standardized["normalized_level"] = "staff"
        else:
            standardized["normalized_level"] = "mid"
        
        return standardized
    def _generate_data_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the dataset."""
        if not data:
            return {}
        
        total_candidates = len(data)
        unique_interviewers = len(set(record["interviewer_id"] for record in data))
        
        # Score statistics
        all_scores = []
        all_average_scores = []
        hire_decisions = []
        
        for record in data:
            all_scores.extend(record["scores"].values())
            all_average_scores.append(record["average_score"])
            hire_decisions.append(record["hire_decision"])
        
        # Date range
        dates = [record["date"] for record in data if record["date"]]
        date_range = {
            "start_date": min(dates).isoformat() if dates else None,
            "end_date": max(dates).isoformat() if dates else None,
            "total_days": (max(dates) - min(dates)).days if len(dates) > 1 else 0
        }
        
        # Role distribution
        roles = [record.get("role", "unknown") for record in data]
        role_distribution = dict(Counter(roles))
        
        return {
            "total_candidates": total_candidates,
            "unique_interviewers": unique_interviewers,
            "candidates_per_interviewer": round(total_candidates / unique_interviewers, 2),
            "date_range": date_range,
            "score_statistics": {
                "mean_individual_scores": round(statistics.mean(all_scores), 2),
                "std_individual_scores": round(statistics.stdev(all_scores) if len(all_scores) > 1 else 0, 2),
                "mean_average_scores": round(statistics.mean(all_average_scores), 2),
                "std_average_scores": round(statistics.stdev(all_average_scores) if len(all_average_scores) > 1 else 0, 2)
            },
            "hire_rate": round(sum(hire_decisions) / len(hire_decisions), 3),
            "role_distribution": role_distribution
        }
