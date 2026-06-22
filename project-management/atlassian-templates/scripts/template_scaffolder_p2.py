# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from template_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from template_scaffolder_p1 import _section, _table, macro_expand, macro_info_panel, macro_note_panel, macro_status, macro_toc, macro_warning_panel, template_decision_log, template_meeting_notes, template_runbook  # noqa: E402,E501
# fmt: on


def template_project_kickoff() -> Dict[str, Any]:
    """Generate project kickoff template."""
    today = datetime.now().strftime("%Y-%m-%d")
    body = macro_toc() + '\n'
    body += _section("Project Overview", _table(
        ["Field", "Value"],
        [["Project Name", ""], ["Start Date", today], ["Target End Date", ""],
         ["Project Lead", ""], ["Sponsor", ""], ["Status", macro_status("KICKOFF", "Blue")]],
    ))
    body += _section("Vision & Goals", '<h3>Vision</h3><p>What does success look like?</p>'
        '<h3>Goals</h3><ol><li><p>Goal 1</p></li><li><p>Goal 2</p></li><li><p>Goal 3</p></li></ol>')
    body += _section("Scope", '<h3>In Scope</h3><ul><li><p></p></li></ul><h3>Out of Scope</h3><ul><li><p></p></li></ul>')
    body += _section("Stakeholders", _table(
        ["Name", "Role", "Responsibility", "Communication Preference"],
        [["", "", "", ""]],
    ))
    body += _section("Timeline & Milestones", _table(
        ["Milestone", "Target Date", "Status"],
        [["Phase 1", "", macro_status("NOT STARTED", "Grey")],
         ["Phase 2", "", macro_status("NOT STARTED", "Grey")]],
    ))
    body += _section("Risks", _table(
        ["Risk", "Likelihood", "Impact", "Mitigation"],
        [["", "High/Medium/Low", "High/Medium/Low", ""]],
    ))
    body += _section("Next Steps", '<ul><li><p></p></li></ul>')

    return {"name": "Project Kickoff", "body": body, "labels": ["project-kickoff", "template"]}
def template_sprint_retro() -> Dict[str, Any]:
    """Generate sprint retrospective template."""
    body = macro_toc() + '\n'
    body += _section("Sprint Info", _table(
        ["Field", "Value"],
        [["Sprint", ""], ["Date Range", ""], ["Facilitator", ""],
         ["Velocity", ""], ["Commitment", ""], ["Completion Rate", ""]],
    ))
    body += _section("What Went Well", '<ul><li><p></p></li></ul>')
    body += _section("What Could Be Improved", '<ul><li><p></p></li></ul>')
    body += _section("Action Items from Last Retro", _table(
        ["Action", "Owner", "Status"],
        [["", "", macro_status("DONE", "Green")], ["", "", macro_status("IN PROGRESS", "Yellow")]],
    ))
    body += _section("New Action Items", _table(
        ["Action", "Owner", "Due Date", "Priority"],
        [["", "", "", "High/Medium/Low"]],
    ))
    body += _section("Team Health Check", macro_info_panel("Rate each area 1-5 (1=needs work, 5=great)") + _table(
        ["Area", "Rating", "Trend", "Notes"],
        [["Teamwork", "", "", ""], ["Delivery", "", "", ""],
         ["Fun", "", "", ""], ["Learning", "", "", ""]],
    ))

    return {"name": "Sprint Retrospective", "body": body, "labels": ["sprint-retro", "agile", "template"]}
def template_how_to_guide() -> Dict[str, Any]:
    """Generate how-to guide template."""
    body = macro_toc() + '\n'
    body += macro_info_panel("This guide explains how to accomplish a specific task.") + '\n'
    body += _section("Overview", '<p>Brief description of what this guide covers and who it is for.</p>')
    body += _section("Prerequisites", '<ul><li><p>Prerequisite 1</p></li><li><p>Prerequisite 2</p></li></ul>')
    body += _section("Step-by-Step Instructions",
        '<h3>Step 1: Title</h3><p>Description of what to do.</p>'
        '<h3>Step 2: Title</h3><p>Description of what to do.</p>'
        '<h3>Step 3: Title</h3><p>Description of what to do.</p>')
    body += _section("Troubleshooting", macro_expand("Common Issues",
        '<h3>Issue 1</h3><p>Solution...</p>'
        '<h3>Issue 2</h3><p>Solution...</p>'))
    body += _section("Related Resources", '<ul><li><p>Link 1</p></li><li><p>Link 2</p></li></ul>')

    return {"name": "How-To Guide", "body": body, "labels": ["how-to", "guide", "template"]}
TEMPLATE_REGISTRY = {
    "meeting-notes": template_meeting_notes,
    "decision-log": template_decision_log,
    "runbook": template_runbook,
    "project-kickoff": template_project_kickoff,
    "sprint-retro": template_sprint_retro,
    "how-to-guide": template_how_to_guide,
}
def build_custom_template(
    sections: List[str],
    macros: List[str],
) -> Dict[str, Any]:
    """Build a custom template from sections and macros."""
    body = ""

    # Add requested macros at the top
    if "toc" in macros:
        body += macro_toc() + '\n'
    if "status" in macros:
        body += '<p>Status: ' + macro_status() + '</p>\n'

    for section in sections:
        section = section.strip()
        if not section:
            continue
        body += _section(section, '<p></p>')

    # Add panels if requested
    if "info" in macros:
        body = macro_info_panel("Add instructions or context here.") + '\n' + body
    if "warning" in macros:
        body += macro_warning_panel("Add warnings here.") + '\n'
    if "note" in macros:
        body += macro_note_panel("Add notes here.") + '\n'

    return {"name": "Custom Template", "body": body, "labels": ["custom", "template"]}
def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"TEMPLATE: {result['name']}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Labels: {', '.join(result.get('labels', []))}")
    lines.append("")
    lines.append("CONFLUENCE STORAGE FORMAT MARKUP")
    lines.append("-" * 30)
    lines.append(result["body"])

    return "\n".join(lines)
def format_json_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format results as JSON."""
    return result
