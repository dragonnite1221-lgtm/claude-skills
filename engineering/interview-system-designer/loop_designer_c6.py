# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin6:
    def _create_multi_day_schedule(self, rounds: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Create a multi-day interview schedule."""
        # Split rounds across days (max 4 hours per day)
        max_daily_minutes = 240
        days = {}
        current_day = 1
        current_day_duration = 0
        current_day_rounds = []
        
        for round_name, round_info in rounds:
            duration = round_info["duration_minutes"] + 15  # Add buffer time
            
            if current_day_duration + duration > max_daily_minutes and current_day_rounds:
                # Finalize current day
                days[f"day_{current_day}"] = self._finalize_day_schedule(current_day_rounds)
                current_day += 1
                current_day_duration = 0
                current_day_rounds = []
            
            current_day_rounds.append((round_name, round_info))
            current_day_duration += duration
        
        # Finalize last day
        if current_day_rounds:
            days[f"day_{current_day}"] = self._finalize_day_schedule(current_day_rounds)
        
        return days
    def _finalize_day_schedule(self, day_rounds: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Finalize the schedule for a specific day."""
        start_time = datetime.strptime("09:00", "%H:%M")
        current_time = start_time
        schedule = []
        
        for round_name, round_info in day_rounds:
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
            current_time = end_time + timedelta(minutes=15)  # 15-min buffer
        
        return {
            "date": "TBD",
            "start_time": start_time.strftime("%H:%M"),
            "end_time": (current_time - timedelta(minutes=15)).strftime("%H:%M"),
            "rounds": schedule
        }
    def _calculate_breaks(self, total_duration: int) -> List[Dict[str, Any]]:
        """Calculate recommended breaks based on total duration."""
        breaks = []
        
        if total_duration >= 120:  # 2+ hours
            breaks.append({"type": "short_break", "duration": 15, "after_minutes": 90})
        
        if total_duration >= 240:  # 4+ hours
            breaks.append({"type": "lunch_break", "duration": 60, "after_minutes": 180})
        
        if total_duration >= 360:  # 6+ hours
            breaks.append({"type": "short_break", "duration": 15, "after_minutes": 300})
        
        return breaks
