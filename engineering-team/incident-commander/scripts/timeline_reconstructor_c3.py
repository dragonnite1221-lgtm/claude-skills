# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin3:
    def _detect_phases(self, events: List[Event]) -> List[Phase]:
        """Detect incident phases based on event patterns."""
        phases = []
        current_phase = None
        phase_events = []
        
        for event in events:
            detected_phase = self._identify_phase(event)
            
            if detected_phase != current_phase:
                # End current phase if exists
                if current_phase and phase_events:
                    phase_obj = Phase(
                        name=current_phase,
                        start_time=phase_events[0].timestamp,
                        end_time=phase_events[-1].timestamp,
                        duration=(phase_events[-1].timestamp - phase_events[0].timestamp).total_seconds() / 60,
                        events=phase_events.copy(),
                        description=self.phase_patterns[current_phase]["description"]
                    )
                    phases.append(phase_obj)
                
                # Start new phase
                current_phase = detected_phase
                phase_events = [event]
            else:
                phase_events.append(event)
        
        # Add final phase
        if current_phase and phase_events:
            phase_obj = Phase(
                name=current_phase,
                start_time=phase_events[0].timestamp,
                end_time=phase_events[-1].timestamp,
                duration=(phase_events[-1].timestamp - phase_events[0].timestamp).total_seconds() / 60,
                events=phase_events,
                description=self.phase_patterns[current_phase]["description"]
            )
            phases.append(phase_obj)
        
        return self._merge_adjacent_phases(phases)
    def _identify_phase(self, event: Event) -> str:
        """Identify which phase an event belongs to."""
        message_lower = event.message.lower()
        
        # Score each phase based on keywords and event type
        phase_scores = {}
        
        for phase_name, pattern_info in self.phase_patterns.items():
            score = 0
            
            # Keyword matching
            for keyword in pattern_info["keywords"]:
                if keyword in message_lower:
                    score += 2
            
            # Event type matching
            if event.type in pattern_info["event_types"]:
                score += 3
            
            # Severity boost for certain phases
            if phase_name == "escalation" and event.severity >= 4:
                score += 2
            
            phase_scores[phase_name] = score
        
        # Return highest scoring phase, default to triage
        if phase_scores and max(phase_scores.values()) > 0:
            return max(phase_scores, key=phase_scores.get)
        
        return "triage"  # Default phase
    def _merge_adjacent_phases(self, phases: List[Phase]) -> List[Phase]:
        """Merge adjacent phases of the same type."""
        if not phases:
            return phases
        
        merged = []
        current_phase = phases[0]
        
        for next_phase in phases[1:]:
            if (next_phase.name == current_phase.name and 
                (next_phase.start_time - current_phase.end_time).total_seconds() < 300):  # 5 min gap
                # Merge phases
                merged_events = current_phase.events + next_phase.events
                current_phase = Phase(
                    name=current_phase.name,
                    start_time=current_phase.start_time,
                    end_time=next_phase.end_time,
                    duration=(next_phase.end_time - current_phase.start_time).total_seconds() / 60,
                    events=merged_events,
                    description=current_phase.description
                )
            else:
                merged.append(current_phase)
                current_phase = next_phase
        
        merged.append(current_phase)
        return merged
