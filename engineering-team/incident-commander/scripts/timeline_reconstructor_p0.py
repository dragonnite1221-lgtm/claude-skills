# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


def format_json_output(result: Dict) -> str:
    """Format result as pretty JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def format_text_output(result: Dict) -> str:
    """Format result as human-readable text."""
    if "error" in result:
        return f"Error: {result['error']}"
    
    timeline = result["timeline"]
    metrics = result["metrics"]
    narrative = result["narrative"]
    
    output = []
    output.append("=" * 80)
    output.append("INCIDENT TIMELINE RECONSTRUCTION")
    output.append("=" * 80)
    output.append("")
    
    # Overview
    time_range = timeline["time_range"]
    output.append("OVERVIEW:")
    output.append(f"  Time Range: {time_range['start']} to {time_range['end']}")
    output.append(f"  Total Duration: {time_range['duration_minutes']} minutes")
    output.append(f"  Total Events: {timeline['total_events']}")
    output.append(f"  Phases Detected: {len(timeline['phases'])}")
    output.append("")
    
    # Phase summary
    output.append("PHASES:")
    for phase in timeline["phases"]:
        output.append(f"  {phase['name'].upper()}:")
        output.append(f"    Start: {phase['start_time']}")
        output.append(f"    Duration: {phase['duration_minutes']} minutes")
        output.append(f"    Events: {phase['event_count']}")
        output.append(f"    Description: {phase['description']}")
        output.append("")
    
    # Key metrics
    if "duration_metrics" in metrics:
        duration_metrics = metrics["duration_metrics"]
        output.append("KEY METRICS:")
        output.append(f"  Time to Mitigation: {duration_metrics.get('time_to_mitigation_minutes', 'N/A')} minutes")
        output.append(f"  Time to Resolution: {duration_metrics.get('time_to_resolution_minutes', 'N/A')} minutes")
        
        if "activity_metrics" in metrics:
            activity = metrics["activity_metrics"]
            output.append(f"  Events per Hour: {activity.get('events_per_hour', 'N/A')}")
            output.append(f"  Unique Sources: {activity.get('unique_sources', 'N/A')}")
        output.append("")
    
    # Narrative
    if "summary" in narrative:
        output.append("INCIDENT NARRATIVE:")
        output.append(narrative["summary"])
        output.append("")
    
    # Gap analysis
    if "gap_analysis" in result and result["gap_analysis"]["gaps"]:
        output.append("GAP ANALYSIS:")
        for gap in result["gap_analysis"]["gaps"][:5]:  # Show first 5 gaps
            output.append(f"  {gap['type'].replace('_', ' ').title()}: {gap['gap_minutes']} min gap (threshold: {gap['threshold_minutes']} min)")
        output.append("")
    
    output.append("=" * 80)
    
    return "\n".join(output)
