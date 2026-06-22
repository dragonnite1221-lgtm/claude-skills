# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


def format_human_readable(loop_data: Dict[str, Any]) -> str:
    """Format the interview loop data in a human-readable format."""
    output = []
    
    # Header
    output.append(f"Interview Loop Design for {loop_data['role']} ({loop_data['level'].title()} Level)")
    output.append("=" * 60)
    
    if loop_data.get('team'):
        output.append(f"Team: {loop_data['team']}")
    
    output.append(f"Generated: {loop_data['generated_at']}")
    output.append(f"Total Duration: {loop_data['total_duration_minutes']} minutes ({loop_data['total_duration_minutes']//60}h {loop_data['total_duration_minutes']%60}m)")
    output.append(f"Total Rounds: {loop_data['total_rounds']}")
    output.append("")
    
    # Interview Rounds
    output.append("INTERVIEW ROUNDS")
    output.append("-" * 40)
    
    sorted_rounds = sorted(loop_data['rounds'].items(), key=lambda x: x[1]['order'])
    for round_name, round_info in sorted_rounds:
        output.append(f"\nRound {round_info['order']}: {round_info['name']}")
        output.append(f"Duration: {round_info['duration_minutes']} minutes")
        output.append(f"Format: {round_info['format'].replace('_', ' ').title()}")
        
        output.append("Objectives:")
        for obj in round_info['objectives']:
            output.append(f"  • {obj}")
        
        output.append("Focus Areas:")
        for area in round_info['focus_areas']:
            output.append(f"  • {area.replace('_', ' ').title()}")
    
    # Suggested Schedule
    output.append("\nSUGGESTED SCHEDULE")
    output.append("-" * 40)
    
    schedule = loop_data['suggested_schedule']
    output.append(f"Schedule Type: {schedule['type'].replace('_', ' ').title()}")
    
    for day_name, day_info in schedule['day_structure'].items():
        output.append(f"\n{day_name.replace('_', ' ').title()}:")
        output.append(f"Time: {day_info['start_time']} - {day_info['end_time']}")
        
        for item in day_info['rounds']:
            if item['type'] == 'interview':
                output.append(f"  {item['start_time']}-{item['end_time']}: {item['title']} ({item['duration_minutes']}min)")
            else:
                output.append(f"  {item['start_time']}-{item['end_time']}: {item['type'].title()} ({item['duration_minutes']}min)")
    
    # Interviewer Requirements
    output.append("\nINTERVIEWER REQUIREMENTS")
    output.append("-" * 40)
    
    for round_name, requirements in loop_data['interviewer_requirements'].items():
        round_display = round_name.split("_", 2)[-1].replace("_", " ").title()
        output.append(f"\n{round_display}:")
        output.append(f"Required Skills: {', '.join(requirements['required_skills'])}")
        output.append(f"Suggested Interviewers: {', '.join(requirements['suggested_interviewers'])}")
        output.append(f"Calibration Level: {requirements['calibration_level'].title()}")
    
    # Scorecard Overview
    output.append("\nSCORECARD TEMPLATE")
    output.append("-" * 40)
    
    scorecard = loop_data['scorecard_template']
    output.append("Scoring Scale:")
    for score, description in scorecard['scoring_scale'].items():
        output.append(f"  {score}: {description}")
    
    output.append("\nEvaluation Dimensions:")
    for dim in scorecard['dimensions']:
        output.append(f"  • {dim['dimension'].replace('_', ' ').title()} (Weight: {dim['weight']})")
    
    # Calibration Notes
    output.append("\nCALIBRATION NOTES")
    output.append("-" * 40)
    
    calibration = loop_data['calibration_notes']
    output.append(f"Hiring Bar: {calibration['hiring_bar_notes']}")
    
    output.append("\nCommon Pitfalls:")
    for pitfall in calibration['common_pitfalls']:
        output.append(f"  • {pitfall}")
    
    return "\n".join(output)
