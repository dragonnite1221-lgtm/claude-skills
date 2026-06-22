# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin6:
    def _extract_key_events(self, events: List[Event]) -> List[Event]:
        """Extract the most important events from a phase."""
        # Sort by severity and timestamp
        sorted_events = sorted(events, key=lambda e: (e.severity, e.timestamp), reverse=True)
        
        # Take top events, but ensure chronological representation
        key_events = []
        
        # Always include first and last events
        if events:
            key_events.append(events[0])
            if len(events) > 1:
                key_events.append(events[-1])
        
        # Add high-severity events
        high_severity_events = [e for e in events if e.severity >= 4]
        key_events.extend(high_severity_events[:3])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_events = []
        for event in key_events:
            event_key = (event.timestamp, event.message)
            if event_key not in seen:
                seen.add(event_key)
                unique_events.append(event)
        
        return sorted(unique_events, key=lambda e: e.timestamp)
    def _create_phase_narrative(self, phase: Phase, key_events: List[Event]) -> str:
        """Create narrative text for a phase."""
        phase_templates = {
            "detection": "The incident was first detected when {first_event}. {additional_details}",
            "triage": "Initial investigation began with {first_event}. The team {investigation_actions}",
            "escalation": "The incident was escalated when {escalation_trigger}. {escalation_actions}",
            "mitigation": "Mitigation efforts started with {first_action}. {mitigation_steps}",
            "resolution": "The incident was resolved when {resolution_event}. {confirmation_steps}",
            "review": "Post-incident review activities included {review_activities}"
        }
        
        template = phase_templates.get(phase.name, "During the {phase_name} phase, {activities}")
        
        if not key_events:
            return f"The {phase.name} phase lasted {phase.duration:.0f} minutes with {len(phase.events)} events."
        
        first_event = key_events[0].message
        
        # Customize based on phase
        if phase.name == "detection":
            return template.format(
                first_event=first_event,
                additional_details=f"This phase lasted {phase.duration:.0f} minutes with {len(phase.events)} total events."
            )
        elif phase.name == "triage":
            actions = [e.message for e in key_events if "investigating" in e.message.lower() or "checking" in e.message.lower()]
            investigation_text = "performed various diagnostic activities" if not actions else f"focused on {actions[0]}"
            return template.format(
                first_event=first_event,
                investigation_actions=investigation_text
            )
        else:
            return f"During the {phase.name} phase ({phase.duration:.0f} minutes), key activities included: {first_event}"
    def _classify_timeline_pattern(self, phases: List[Phase]) -> str:
        """Classify the overall timeline pattern."""
        phase_names = [p.name for p in phases]
        
        if "escalation" in phase_names and phases[0].name == "detection":
            return "standard_escalation"
        elif len(phases) <= 3:
            return "simple_resolution"
        elif "review" in phase_names:
            return "comprehensive_response"
        else:
            return "complex_incident"
    def _calculate_complexity_score(self, events: List[Event], phases: List[Phase]) -> float:
        """Calculate incident complexity score (0-10)."""
        score = 0.0
        
        # Phase count contributes to complexity
        score += min(len(phases) * 1.5, 6.0)
        
        # Event count contributes to complexity
        score += min(len(events) / 20, 2.0)
        
        # Duration contributes to complexity
        if events:
            duration_hours = (events[-1].timestamp - events[0].timestamp).total_seconds() / 3600
            score += min(duration_hours / 2, 2.0)
        
        return min(score, 10.0)
