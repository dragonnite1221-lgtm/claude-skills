# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin8:
    def _generate_logistics_notes(self, rounds: List[Tuple[str, Dict]]) -> List[str]:
        """Generate logistics and coordination notes."""
        notes = [
            "Coordinate interviewer availability before scheduling",
            "Ensure all interviewers have access to job description and competency requirements",
            "Prepare interview rooms/virtual links for all rounds",
            "Share candidate resume and application with all interviewers"
        ]
        
        # Add format-specific notes
        formats_used = {round_info["format"] for _, round_info in rounds}
        
        if "virtual" in formats_used:
            notes.append("Test video conferencing setup before virtual interviews")
            notes.append("Share virtual meeting links with candidate 24 hours in advance")
        
        if "collaborative_whiteboard" in formats_used:
            notes.append("Prepare whiteboard or collaborative online tool for design sessions")
        
        if "hands_on_design" in formats_used:
            notes.append("Provide design tools access or ensure candidate can screen share their preferred tools")
        
        return notes
