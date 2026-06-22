# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from template_scaffolder_base import *  # noqa: F403,E402


def macro_toc() -> str:
    """Generate table of contents macro."""
    return '<ac:structured-macro ac:name="toc"><ac:parameter ac:name="printable">true</ac:parameter><ac:parameter ac:name="style">disc</ac:parameter><ac:parameter ac:name="maxLevel">3</ac:parameter></ac:structured-macro>'
def macro_status(text: str = "IN PROGRESS", color: str = "Yellow") -> str:
    """Generate status macro."""
    return f'<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">{color}</ac:parameter><ac:parameter ac:name="title">{text}</ac:parameter></ac:structured-macro>'
def macro_info_panel(content: str) -> str:
    """Generate info panel macro."""
    return f'<ac:structured-macro ac:name="info"><ac:rich-text-body><p>{content}</p></ac:rich-text-body></ac:structured-macro>'
def macro_warning_panel(content: str) -> str:
    """Generate warning panel macro."""
    return f'<ac:structured-macro ac:name="warning"><ac:rich-text-body><p>{content}</p></ac:rich-text-body></ac:structured-macro>'
def macro_note_panel(content: str) -> str:
    """Generate note panel macro."""
    return f'<ac:structured-macro ac:name="note"><ac:rich-text-body><p>{content}</p></ac:rich-text-body></ac:structured-macro>'
def macro_expand(title: str, content: str) -> str:
    """Generate expand/collapse macro."""
    return f'<ac:structured-macro ac:name="expand"><ac:parameter ac:name="title">{title}</ac:parameter><ac:rich-text-body>{content}</ac:rich-text-body></ac:structured-macro>'
def macro_jira_issues(jql: str) -> str:
    """Generate Jira issues macro."""
    return f'<ac:structured-macro ac:name="jira"><ac:parameter ac:name="jqlQuery">{jql}</ac:parameter><ac:parameter ac:name="columns">key,summary,type,created,updated,due,assignee,reporter,priority,status,resolution</ac:parameter></ac:structured-macro>'
MACRO_MAP = {
    "toc": macro_toc,
    "status": macro_status,
    "info": macro_info_panel,
    "warning": macro_warning_panel,
    "note": macro_note_panel,
    "expand": macro_expand,
    "jira-issues": macro_jira_issues,
}
def _section(title: str, content: str) -> str:
    """Generate a section with heading and content."""
    return f'<h2>{title}</h2>\n{content}\n'
def _table(headers: List[str], rows: List[List[str]]) -> str:
    """Generate an XHTML table."""
    parts = ['<table><colgroup>']
    for _ in headers:
        parts.append('<col />')
    parts.append('</colgroup><thead><tr>')
    for h in headers:
        parts.append(f'<th><p>{h}</p></th>')
    parts.append('</tr></thead><tbody>')
    for row in rows:
        parts.append('<tr>')
        for cell in row:
            parts.append(f'<td><p>{cell}</p></td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return ''.join(parts)
def template_meeting_notes() -> Dict[str, Any]:
    """Generate meeting notes template."""
    today = datetime.now().strftime("%Y-%m-%d")
    body = macro_toc() + '\n'
    body += macro_info_panel("Replace placeholder text with your meeting details.") + '\n'
    body += _section("Meeting Details", _table(
        ["Field", "Value"],
        [["Date", today], ["Time", ""], ["Location", ""], ["Facilitator", ""], ["Note Taker", ""]],
    ))
    body += _section("Attendees", '<ul><li><p>Name 1</p></li><li><p>Name 2</p></li></ul>')
    body += _section("Agenda", '<ol><li><p>Item 1</p></li><li><p>Item 2</p></li><li><p>Item 3</p></li></ol>')
    body += _section("Discussion Notes", '<p>Summary of discussion points...</p>')
    body += _section("Decisions Made", _table(
        ["Decision", "Owner", "Date"],
        [["", "", today]],
    ))
    body += _section("Action Items", _table(
        ["Action", "Owner", "Due Date", "Status"],
        [["", "", "", macro_status("TODO", "Grey")]],
    ))
    body += _section("Next Meeting", '<p>Date: TBD</p><p>Agenda items for next time:</p><ul><li><p></p></li></ul>')

    return {"name": "Meeting Notes", "body": body, "labels": ["meeting-notes", "template"]}
def template_decision_log() -> Dict[str, Any]:
    """Generate decision log template."""
    today = datetime.now().strftime("%Y-%m-%d")
    body = macro_toc() + '\n'
    body += _section("Decision Log", macro_info_panel("Track key decisions, context, and outcomes."))
    body += _table(
        ["ID", "Date", "Decision", "Context", "Alternatives Considered", "Outcome", "Owner", "Status"],
        [
            ["D-001", today, "", "", "", "", "", macro_status("DECIDED", "Green")],
            ["D-002", "", "", "", "", "", "", macro_status("PENDING", "Yellow")],
        ],
    )
    body += '\n'
    body += _section("Decision Template", macro_expand("Decision Details Template",
        '<h3>Context</h3><p>What is the issue or situation requiring a decision?</p>'
        '<h3>Options</h3><ol><li><p>Option A - pros/cons</p></li><li><p>Option B - pros/cons</p></li></ol>'
        '<h3>Decision</h3><p>What was decided and why?</p>'
        '<h3>Consequences</h3><p>What are the expected outcomes?</p>'
    ))

    return {"name": "Decision Log", "body": body, "labels": ["decision-log", "template"]}
def template_runbook() -> Dict[str, Any]:
    """Generate runbook template."""
    body = macro_toc() + '\n'
    body += macro_warning_panel("This runbook should be tested and reviewed quarterly.") + '\n'
    body += _section("Overview", '<p>Brief description of what this runbook covers.</p>'
        + _table(["Field", "Value"], [
            ["Service/System", ""], ["Owner", ""], ["Last Tested", ""],
            ["Severity", ""], ["Estimated Duration", ""],
        ]))
    body += _section("Prerequisites", '<ul><li><p>Access to system X</p></li><li><p>VPN connected</p></li><li><p>Required tools installed</p></li></ul>')
    body += _section("Steps", '<ol><li><p><strong>Step 1:</strong> Description</p><ac:structured-macro ac:name="code"><ac:parameter ac:name="language">bash</ac:parameter><ac:plain-text-body><![CDATA[# command here]]></ac:plain-text-body></ac:structured-macro></li>'
        '<li><p><strong>Step 2:</strong> Description</p></li>'
        '<li><p><strong>Step 3:</strong> Description</p></li></ol>')
    body += _section("Verification", '<p>How to verify the issue is resolved:</p><ul><li><p>Check 1</p></li><li><p>Check 2</p></li></ul>')
    body += _section("Rollback", macro_note_panel("If the above steps do not resolve the issue, follow these rollback steps.") +
        '<ol><li><p>Rollback step 1</p></li><li><p>Rollback step 2</p></li></ol>')
    body += _section("Escalation", _table(
        ["Level", "Contact", "When to Escalate"],
        [["L1", "", ""], ["L2", "", ""], ["L3", "", ""]],
    ))

    return {"name": "Runbook", "body": body, "labels": ["runbook", "operations", "template"]}
