# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from timeline_reconstructor_base import *  # noqa: F403,E402


def format_markdown_output(result: Dict) -> str:
    """Format result as Markdown timeline."""
    if "error" in result:
        return f"# Error\n\n{result['error']}"
    
    timeline = result["timeline"]
    narrative = result.get("narrative", {})
    
    output = []
    output.append("# Incident Timeline")
    output.append("")
    
    # Overview
    time_range = timeline["time_range"]
    output.append("## Overview")
    output.append("")
    output.append(f"- **Duration:** {time_range['duration_minutes']} minutes")
    output.append(f"- **Start Time:** {time_range['start']}")
    output.append(f"- **End Time:** {time_range['end']}")
    output.append(f"- **Total Events:** {timeline['total_events']}")
    output.append("")
    
    # Narrative summary
    if "summary" in narrative:
        output.append("## Summary")
        output.append("")
        output.append(narrative["summary"])
        output.append("")
    
    # Phase timeline
    output.append("## Phase Timeline")
    output.append("")
    
    for phase in timeline["phases"]:
        output.append(f"### {phase['name'].title()} Phase")
        output.append("")
        output.append(f"**Duration:** {phase['duration_minutes']} minutes  ")
        output.append(f"**Start:** {phase['start_time']}  ")
        output.append(f"**Events:** {phase['event_count']}  ")
        output.append("")
        output.append(phase["description"])
        output.append("")
    
    # Detailed timeline
    output.append("## Detailed Event Timeline")
    output.append("")
    
    for event in timeline["events"]:
        timestamp = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
        output.append(f"**{timestamp.strftime('%H:%M:%S')}** [{event['source']}] {event['message']}")
        output.append("")
    
    return "\n".join(output)
