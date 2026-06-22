# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin7:
    def _generate_summary(self, events: List[Event], phases: List[Phase], metrics: Dict) -> Dict[str, Any]:
        """Generate comprehensive incident summary."""
        if not events:
            return {}
        
        # Key statistics
        start_time = events[0].timestamp
        end_time = events[-1].timestamp
        duration_minutes = metrics.get("duration_metrics", {}).get("total_duration_minutes", 0)
        
        # Phase analysis
        phase_analysis = {}
        for phase in phases:
            phase_analysis[phase.name] = {
                "duration_minutes": round(phase.duration, 1),
                "event_count": len(phase.events),
                "start_time": phase.start_time.isoformat(),
                "end_time": phase.end_time.isoformat()
            }
        
        # Actor involvement
        actors = defaultdict(int)
        for event in events:
            actors[event.actor] += 1
        
        return {
            "incident_overview": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_minutes": round(duration_minutes, 1),
                "total_events": len(events),
                "phases_detected": len(phases)
            },
            "phase_analysis": phase_analysis,
            "key_participants": dict(actors),
            "event_sources": dict(defaultdict(int, {e.source: 1 for e in events})),
            "complexity_indicators": {
                "unique_sources": len(set(e.source for e in events)),
                "unique_actors": len(set(e.actor for e in events)),
                "high_severity_events": len([e for e in events if e.severity >= 4]),
                "phase_transitions": len(phases) - 1 if phases else 0
            }
        }
    def _event_to_dict(self, event: Event) -> Dict:
        """Convert Event namedtuple to dictionary."""
        return {
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "type": event.type,
            "message": event.message,
            "severity": event.severity,
            "actor": event.actor,
            "metadata": event.metadata
        }
    def _phase_to_dict(self, phase: Phase) -> Dict:
        """Convert Phase namedtuple to dictionary."""
        return {
            "name": phase.name,
            "start_time": phase.start_time.isoformat(),
            "end_time": phase.end_time.isoformat(),
            "duration_minutes": round(phase.duration, 1),
            "event_count": len(phase.events),
            "description": phase.description
        }
