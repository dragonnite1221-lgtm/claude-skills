# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gws_recipe_runner_base import *  # noqa: F403,E402
# fmt: off
from gws_recipe_runner_p1 import Recipe  # noqa: E402,E501
# fmt: on


RECIPES: Dict[str, Recipe] = {
    # Email (8)
    "send-email": Recipe("send-email", "Send an email with optional attachments", "email",
                         ["gmail"], ["gws gmail users.messages send me --to {to} --subject {subject} --body {body}"]),
    "reply-to-thread": Recipe("reply-to-thread", "Reply to an existing email thread", "email",
                              ["gmail"], ["gws gmail users.messages reply me --thread-id {thread_id} --body {body}"]),
    "forward-email": Recipe("forward-email", "Forward an email to another recipient", "email",
                            ["gmail"], ["gws gmail users.messages forward me --message-id {msg_id} --to {to}"]),
    "search-emails": Recipe("search-emails", "Search emails with Gmail query syntax", "email",
                            ["gmail"], ["gws gmail users.messages list me --query {query} --json"]),
    "archive-old": Recipe("archive-old", "Archive read emails older than N days", "email",
                          ["gmail"], [
                              "gws gmail users.messages list me --query 'is:read older_than:{days}d' --json",
                              "# Pipe IDs to batch modify to remove INBOX label",
                          ]),
    "label-manager": Recipe("label-manager", "Create, list, and organize Gmail labels", "email",
                            ["gmail"], ["gws gmail users.labels list me --json", "gws gmail users.labels create me --name {name}"]),
    "filter-setup": Recipe("filter-setup", "Create email filters for auto-labeling", "email",
                           ["gmail"], ["gws gmail users.settings.filters create me --criteria {criteria} --action {action}"]),
    "unread-digest": Recipe("unread-digest", "Get digest of unread emails", "email",
                            ["gmail"], ["gws gmail users.messages list me --query 'is:unread' --limit 20 --json"]),

    # Files (7)
    "upload-file": Recipe("upload-file", "Upload a file to Google Drive", "files",
                          ["drive"], ["gws drive files create --name {name} --upload {path} --parents {folder_id}"]),
    "create-sheet": Recipe("create-sheet", "Create a new Google Spreadsheet", "files",
                           ["sheets"], ["gws sheets spreadsheets create --title {title} --json"]),
    "share-file": Recipe("share-file", "Share a Drive file with a user or domain", "files",
                          ["drive"], ["gws drive permissions create {file_id} --type user --role writer --emailAddress {email}"]),
    "export-file": Recipe("export-file", "Export a Google Doc/Sheet as PDF", "files",
                          ["drive"], ["gws drive files export {file_id} --mime application/pdf --output {output}"]),
    "list-files": Recipe("list-files", "List files in a Drive folder", "files",
                         ["drive"], ["gws drive files list --parents {folder_id} --json"]),
    "find-large-files": Recipe("find-large-files", "Find largest files in Drive", "files",
                               ["drive"], ["gws drive files list --orderBy 'quotaBytesUsed desc' --limit 20 --json"]),
    "cleanup-trash": Recipe("cleanup-trash", "Empty Drive trash", "files",
                            ["drive"], ["gws drive files emptyTrash"]),

    # Calendar (6)
    "create-event": Recipe("create-event", "Create a calendar event with attendees", "calendar",
                           ["calendar"], [
                               "gws calendar events insert primary --summary {title} "
                               "--start {start} --end {end} --attendees {attendees}"
                           ]),
    "quick-event": Recipe("quick-event", "Create event from natural language", "calendar",
                          ["calendar"], ["gws helpers quick-event {text}"]),
    "find-time": Recipe("find-time", "Find available time slots for a meeting", "calendar",
                        ["calendar"], ["gws helpers find-time --attendees {attendees} --duration {minutes} --within {date_range}"]),
    "today-schedule": Recipe("today-schedule", "Show today's calendar events", "calendar",
                             ["calendar"], ["gws calendar events list primary --timeMin {today_start} --timeMax {today_end} --json"]),
    "meeting-prep": Recipe("meeting-prep", "Prepare for an upcoming meeting (agenda + attendees)", "calendar",
                           ["calendar"], ["gws recipes meeting-prep --event-id {event_id}"]),
    "reschedule": Recipe("reschedule", "Move an event to a new time", "calendar",
                         ["calendar"], ["gws calendar events patch primary {event_id} --start {new_start} --end {new_end}"]),

    # Reporting (5)
    "standup-report": Recipe("standup-report", "Generate daily standup from calendar and tasks", "reporting",
                             ["calendar", "tasks"], ["gws recipes standup-report --json"]),
    "weekly-summary": Recipe("weekly-summary", "Summarize week's emails, events, and tasks", "reporting",
                             ["gmail", "calendar", "tasks"], ["gws recipes weekly-summary --json"]),
    "drive-activity": Recipe("drive-activity", "Report on Drive file activity", "reporting",
                             ["drive"], ["gws drive activities list --json"]),
    "email-stats": Recipe("email-stats", "Email volume statistics", "reporting",
                          ["gmail"], [
                              "gws gmail users.messages list me --query 'newer_than:7d' --json",
                              "# Pipe through output_analyzer.py --count",
                          ]),
    "task-progress": Recipe("task-progress", "Report on task completion", "reporting",
                            ["tasks"], ["gws tasks tasks list {tasklist_id} --json"]),

    # Collaboration (5)
    "share-folder": Recipe("share-folder", "Share a Drive folder with a team", "collaboration",
                           ["drive"], ["gws drive permissions create {folder_id} --type group --role writer --emailAddress {group}"]),
    "create-doc": Recipe("create-doc", "Create a Google Doc with initial content", "collaboration",
                         ["docs"], ["gws docs documents create --title {title} --json"]),
    "chat-message": Recipe("chat-message", "Send a message to a Google Chat space", "collaboration",
                           ["chat"], ["gws chat spaces.messages create {space} --text {message}"]),
    "list-spaces": Recipe("list-spaces", "List Google Chat spaces", "collaboration",
                          ["chat"], ["gws chat spaces list --json"]),
    "task-create": Recipe("task-create", "Create a task in Google Tasks", "collaboration",
                          ["tasks"], ["gws tasks tasks insert {tasklist_id} --title {title} --due {due_date}"]),

    # Data (4)
    "sheet-read": Recipe("sheet-read", "Read data from a spreadsheet range", "data",
                         ["sheets"], ["gws sheets spreadsheets.values get {sheet_id} --range {range} --json"]),
    "sheet-write": Recipe("sheet-write", "Write data to a spreadsheet", "data",
                          ["sheets"], ["gws sheets spreadsheets.values update {sheet_id} --range {range} --values {data}"]),
    "sheet-append": Recipe("sheet-append", "Append rows to a spreadsheet", "data",
                           ["sheets"], ["gws sheets spreadsheets.values append {sheet_id} --range {range} --values {data}"]),
    "export-contacts": Recipe("export-contacts", "Export contacts list", "data",
                              ["people"], ["gws people people.connections list me --personFields names,emailAddresses --json"]),

    # Admin (4)
    "list-users": Recipe("list-users", "List all users in the Workspace domain", "admin",
                         ["admin"], ["gws admin users list --domain {domain} --json"],
                         "Requires Admin SDK API and admin.directory.user.readonly scope"),
    "list-groups": Recipe("list-groups", "List all groups in the domain", "admin",
                          ["admin"], ["gws admin groups list --domain {domain} --json"]),
    "user-info": Recipe("user-info", "Get detailed user information", "admin",
                        ["admin"], ["gws admin users get {email} --json"]),
    "audit-logins": Recipe("audit-logins", "Audit recent login activity", "admin",
                           ["admin"], ["gws admin activities list login --json"]),

    # Cross-Service (4)
    "morning-briefing": Recipe("morning-briefing", "Today's events + unread emails + pending tasks", "cross-service",
                               ["gmail", "calendar", "tasks"], [
                                   "gws calendar events list primary --timeMin {today} --maxResults 10 --json",
                                   "gws gmail users.messages list me --query 'is:unread' --limit 10 --json",
                                   "gws tasks tasks list {default_tasklist} --json",
                               ]),
    "eod-wrap": Recipe("eod-wrap", "End-of-day wrap up: summarize completed, pending, tomorrow", "cross-service",
                       ["calendar", "tasks"], [
                           "gws calendar events list primary --timeMin {today_start} --timeMax {today_end} --json",
                           "gws tasks tasks list {default_tasklist} --json",
                       ]),
    "project-status": Recipe("project-status", "Aggregate project status from Drive, Sheets, Tasks", "cross-service",
                             ["drive", "sheets", "tasks"], [
                                 "gws drive files list --query 'name contains {project}' --json",
                                 "gws tasks tasks list {tasklist_id} --json",
                             ]),
    "inbox-zero": Recipe("inbox-zero", "Process inbox to zero: label, archive, reply, task", "cross-service",
                         ["gmail", "tasks"], [
                             "gws gmail users.messages list me --query 'is:inbox' --json",
                             "# Process each: label, archive, or create task",
                         ]),
}
