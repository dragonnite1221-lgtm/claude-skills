# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


class TimelineReconstructorMixin5:
    def _analyze_gaps(self, events: List[Event], phases: List[Phase]) -> Dict[str, Any]:
        """Perform gap analysis to identify potential issues."""
        gaps = []
        warnings = []
        
        # Check phase transition timing
        for i in range(len(phases) - 1):
            current_phase = phases[i]
            next_phase = phases[i + 1]
            
            transition_gap = (next_phase.start_time - current_phase.end_time).total_seconds() / 60
            threshold_key = f"{current_phase.name}_to_{next_phase.name}"
            threshold = self.gap_thresholds.get(threshold_key, self.gap_thresholds["phase_transition"])
            
            if transition_gap > threshold:
                gaps.append({
                    "type": "phase_transition",
                    "from_phase": current_phase.name,
                    "to_phase": next_phase.name,
                    "gap_minutes": round(transition_gap, 1),
                    "threshold_minutes": threshold,
                    "severity": "warning" if transition_gap < threshold * 2 else "critical"
                })
        
        # Check communication gaps
        comm_events = [e for e in events if e.type == "communication"]
        for i in range(len(comm_events) - 1):
            gap_minutes = (comm_events[i+1].timestamp - comm_events[i].timestamp).total_seconds() / 60
            if gap_minutes > self.gap_thresholds["communication_gap"]:
                gaps.append({
                    "type": "communication_gap",
                    "gap_minutes": round(gap_minutes, 1),
                    "threshold_minutes": self.gap_thresholds["communication_gap"],
                    "severity": "warning" if gap_minutes < self.gap_thresholds["communication_gap"] * 2 else "critical"
                })
        
        # Check for missing phases
        expected_phases = ["detection", "triage", "mitigation", "resolution"]
        actual_phases = [p.name for p in phases]
        missing_phases = [p for p in expected_phases if p not in actual_phases]
        
        for missing_phase in missing_phases:
            warnings.append({
                "type": "missing_phase",
                "phase": missing_phase,
                "message": f"Expected phase '{missing_phase}' not detected in timeline"
            })
        
        # Check for unusually long phases
        for phase in phases:
            if phase.duration > 180:  # 3 hours
                warnings.append({
                    "type": "long_phase",
                    "phase": phase.name,
                    "duration_minutes": round(phase.duration, 1),
                    "message": f"Phase '{phase.name}' lasted {phase.duration:.0f} minutes, which is unusually long"
                })
        
        return {
            "gaps": gaps,
            "warnings": warnings,
            "gap_summary": {
                "total_gaps": len(gaps),
                "critical_gaps": len([g for g in gaps if g.get("severity") == "critical"]),
                "warning_gaps": len([g for g in gaps if g.get("severity") == "warning"]),
                "missing_phases": len(missing_phases)
            }
        }
    def _generate_narrative(self, events: List[Event], phases: List[Phase]) -> Dict[str, Any]:
        """Generate human-readable incident narrative."""
        if not events or not phases:
            return {"error": "Insufficient data for narrative generation"}
        
        # Create phase-based narrative
        phase_narratives = []
        for phase in phases:
            key_events = self._extract_key_events(phase.events)
            narrative_text = self._create_phase_narrative(phase, key_events)
            
            phase_narratives.append({
                "phase": phase.name,
                "start_time": phase.start_time.isoformat(),
                "duration_minutes": round(phase.duration, 1),
                "narrative": narrative_text,
                "key_events": len(key_events),
                "total_events": len(phase.events)
            })
        
        # Create overall summary
        start_time = events[0].timestamp
        end_time = events[-1].timestamp
        total_duration = (end_time - start_time).total_seconds() / 60
        
        summary = f"""Incident Timeline Summary:
The incident began at {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} and concluded at {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}, lasting approximately {total_duration:.0f} minutes.

The incident progressed through {len(phases)} distinct phases: {', '.join(p.name for p in phases)}.

Key milestones:"""
        
        for phase in phases:
            summary += f"\n- {phase.name.title()}: {phase.start_time.strftime('%H:%M')} ({phase.duration:.0f} min)"
        
        return {
            "summary": summary,
            "phase_narratives": phase_narratives,
            "timeline_type": self._classify_timeline_pattern(phases),
            "complexity_score": self._calculate_complexity_score(events, phases)
        }
