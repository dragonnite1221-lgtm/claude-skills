# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin5:
    def _customize_focus_areas(self, round_type: str, competency_req: Dict, 
                              custom_competencies: Optional[List[str]]) -> List[str]:
        """Customize focus areas based on role competency requirements."""
        base_focus_areas = competency_req.get("focus_areas", [])
        
        round_focus_mapping = {
            "technical_phone_screen": ["coding_fundamentals", "problem_solving"],
            "coding_deep_dive": ["technical_execution", "code_quality"],
            "system_design": ["system_thinking", "architectural_reasoning"],
            "behavioral": ["cultural_fit", "communication", "teamwork"],
            "technical_leadership": ["leadership", "mentoring", "influence"],
            "product_sense": ["product_intuition", "user_empathy"],
            "analytical_thinking": ["data_analysis", "metric_design"],
            "design_challenge": ["design_process", "user_focus"]
        }
        
        focus_areas = round_focus_mapping.get(round_type, [])
        
        # Add custom competencies if specified
        if custom_competencies:
            focus_areas.extend([comp for comp in custom_competencies if comp not in focus_areas])
        
        # Add role-specific focus areas
        focus_areas.extend([area for area in base_focus_areas if area not in focus_areas])
        
        return focus_areas[:5]  # Limit to top 5 focus areas
    def _create_schedule(self, rounds: Dict[str, Dict]) -> Dict[str, Any]:
        """Create a suggested interview schedule."""
        sorted_rounds = sorted(rounds.items(), key=lambda x: x[1]["order"])
        
        # Calculate optimal scheduling
        total_duration = sum(round_info["duration_minutes"] for _, round_info in sorted_rounds)
        
        if total_duration <= 240:  # 4 hours or less - single day
            schedule_type = "single_day"
            day_structure = self._create_single_day_schedule(sorted_rounds)
        else:  # Multi-day schedule
            schedule_type = "multi_day"
            day_structure = self._create_multi_day_schedule(sorted_rounds)
        
        return {
            "type": schedule_type,
            "total_duration_minutes": total_duration,
            "recommended_breaks": self._calculate_breaks(total_duration),
            "day_structure": day_structure,
            "logistics_notes": self._generate_logistics_notes(sorted_rounds)
        }
    def _create_single_day_schedule(self, rounds: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Create a single-day interview schedule."""
        start_time = datetime.strptime("09:00", "%H:%M")
        current_time = start_time
        
        schedule = []
        
        for round_name, round_info in rounds:
            # Add break if needed (after 90 minutes of interviews)
            if schedule and sum(item.get("duration_minutes", 0) for item in schedule if "break" not in item.get("type", "")) >= 90:
                schedule.append({
                    "type": "break",
                    "start_time": current_time.strftime("%H:%M"),
                    "duration_minutes": 15,
                    "end_time": (current_time + timedelta(minutes=15)).strftime("%H:%M")
                })
                current_time += timedelta(minutes=15)
            
            # Add the interview round
            end_time = current_time + timedelta(minutes=round_info["duration_minutes"])
            schedule.append({
                "type": "interview",
                "round_name": round_name,
                "title": round_info["name"],
                "start_time": current_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "duration_minutes": round_info["duration_minutes"],
                "format": round_info["format"]
            })
            current_time = end_time
        
        return {
            "day_1": {
                "date": "TBD",
                "start_time": start_time.strftime("%H:%M"),
                "end_time": current_time.strftime("%H:%M"),
                "rounds": schedule
            }
        }
