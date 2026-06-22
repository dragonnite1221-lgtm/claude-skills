# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin4:
    def _calculate_metrics(self, events: List[Event], phases: List[Phase]) -> Dict[str, Any]:
        """Calculate timeline metrics and KPIs."""
        if not events or not phases:
            return {}
        
        start_time = events[0].timestamp
        end_time = events[-1].timestamp
        total_duration = (end_time - start_time).total_seconds() / 60
        
        # Phase timing metrics
        phase_durations = {phase.name: phase.duration for phase in phases}
        
        # Detection metrics
        detection_time = 0
        if phases and phases[0].name == "detection":
            detection_time = phases[0].duration
        
        # Time to mitigation
        mitigation_start = None
        for phase in phases:
            if phase.name == "mitigation":
                mitigation_start = (phase.start_time - start_time).total_seconds() / 60
                break
        
        # Time to resolution
        resolution_time = None
        for phase in phases:
            if phase.name == "resolution":
                resolution_time = (phase.start_time - start_time).total_seconds() / 60
                break
        
        # Communication frequency
        comm_events = [e for e in events if e.type == "communication"]
        comm_frequency = len(comm_events) / (total_duration / 60) if total_duration > 0 else 0
        
        # Action frequency
        action_events = [e for e in events if e.type == "action"]
        action_frequency = len(action_events) / (total_duration / 60) if total_duration > 0 else 0
        
        # Event source distribution
        source_counts = defaultdict(int)
        for event in events:
            source_counts[event.source] += 1
        
        return {
            "duration_metrics": {
                "total_duration_minutes": round(total_duration, 1),
                "detection_duration_minutes": round(detection_time, 1),
                "time_to_mitigation_minutes": round(mitigation_start or 0, 1),
                "time_to_resolution_minutes": round(resolution_time or 0, 1),
                "phase_durations": {k: round(v, 1) for k, v in phase_durations.items()}
            },
            "activity_metrics": {
                "total_events": len(events),
                "events_per_hour": round((len(events) / (total_duration / 60)) if total_duration > 0 else 0, 1),
                "communication_frequency": round(comm_frequency, 1),
                "action_frequency": round(action_frequency, 1),
                "unique_sources": len(source_counts),
                "unique_actors": len(set(e.actor for e in events))
            },
            "phase_metrics": {
                "total_phases": len(phases),
                "phase_sequence": [p.name for p in phases],
                "longest_phase": max(phases, key=lambda p: p.duration).name if phases else None,
                "shortest_phase": min(phases, key=lambda p: p.duration).name if phases else None
            },
            "source_distribution": dict(source_counts)
        }
