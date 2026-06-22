# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin1:
    def _load_severity_mapping(self) -> Dict[str, int]:
        """Load severity level mappings."""
        return {
            "critical": 5, "crit": 5, "sev1": 5, "p1": 5,
            "high": 4, "major": 4, "sev2": 4, "p2": 4,
            "medium": 3, "moderate": 3, "sev3": 3, "p3": 3,
            "low": 2, "minor": 2, "sev4": 2, "p4": 2,
            "info": 1, "informational": 1, "debug": 1,
            "unknown": 0
        }
    def _load_gap_thresholds(self) -> Dict[str, int]:
        """Load gap analysis thresholds in minutes."""
        return {
            "detection_to_triage": 15,  # Should start investigating within 15 min
            "triage_to_mitigation": 30,  # Should start mitigation within 30 min
            "mitigation_to_resolution": 120,  # Should resolve within 2 hours
            "communication_gap": 30,  # Should communicate every 30 min
            "action_gap": 60,  # Should take actions every hour
            "phase_transition": 45  # Should transition phases within 45 min
        }
    def reconstruct_timeline(self, events_data: List[Dict]) -> Dict[str, Any]:
        """
        Main reconstruction method that processes events and builds timeline.
        
        Args:
            events_data: List of event dictionaries
            
        Returns:
            Dictionary with timeline analysis and metrics
        """
        # Parse and normalize events
        events = self._parse_events(events_data)
        if not events:
            return {"error": "No valid events found"}
        
        # Sort events chronologically
        events.sort(key=lambda e: e.timestamp)
        
        # Detect phases
        phases = self._detect_phases(events)
        
        # Calculate metrics
        metrics = self._calculate_metrics(events, phases)
        
        # Perform gap analysis
        gap_analysis = self._analyze_gaps(events, phases)
        
        # Generate timeline narrative
        narrative = self._generate_narrative(events, phases)
        
        # Create summary statistics
        summary = self._generate_summary(events, phases, metrics)
        
        return {
            "timeline": {
                "total_events": len(events),
                "time_range": {
                    "start": events[0].timestamp.isoformat(),
                    "end": events[-1].timestamp.isoformat(),
                    "duration_minutes": int((events[-1].timestamp - events[0].timestamp).total_seconds() / 60)
                },
                "phases": [self._phase_to_dict(phase) for phase in phases],
                "events": [self._event_to_dict(event) for event in events]
            },
            "metrics": metrics,
            "gap_analysis": gap_analysis,
            "narrative": narrative,
            "summary": summary,
            "reconstruction_timestamp": datetime.now(timezone.utc).isoformat()
        }
