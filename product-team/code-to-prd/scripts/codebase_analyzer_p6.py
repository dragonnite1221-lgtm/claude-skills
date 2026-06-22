# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402
# fmt: off
from codebase_analyzer_p5 import analyze_project  # noqa: E402,E501
# fmt: on


def format_markdown(analysis: Dict[str, Any]) -> str:
    """Format analysis as markdown summary."""
    lines = []
    proj = analysis["project"]
    summary = analysis["summary"]
    stack = summary.get("stack_type", "frontend")

    lines.append(f"# Codebase Analysis: {proj['name'] or 'Project'}")
    lines.append("")
    lines.append(f"**Framework:** {proj['framework']}")
    lines.append(f"**Stack type:** {stack}")
    lines.append(f"**Total files:** {analysis['structure']['total_files']}")
    if summary.get("pages"):
        lines.append(f"**Frontend pages:** {summary['pages']}")
    if summary.get("backend_endpoints"):
        lines.append(f"**Backend endpoints:** {summary['backend_endpoints']}")
    lines.append(f"**API calls detected:** {summary['api_endpoints']} "
                 f"({summary['api_integrated']} integrated, {summary['api_mock']} mock)")
    lines.append(f"**Enums:** {summary['enums']}")
    if summary.get("models"):
        lines.append(f"**Models/entities:** {summary['models']}")
    lines.append(f"**i18n:** {'Yes' if summary['has_i18n'] else 'No'}")
    lines.append(f"**State management:** {'Yes' if summary['has_state_management'] else 'No'}")
    lines.append("")

    if analysis["routes"]["pages"]:
        lines.append("## Pages / Routes")
        lines.append("")
        lines.append("| # | Route | Source |")
        lines.append("|---|-------|--------|")
        for i, r in enumerate(analysis["routes"]["pages"], 1):
            src = r.get("source", "").split("/")[-1]
            fs = " (fs)" if r.get("filesystem") else ""
            lines.append(f"| {i} | `{r['path']}` | {src}{fs} |")
        lines.append("")

    if analysis["apis"]["endpoints"]:
        lines.append("## API Endpoints")
        lines.append("")
        lines.append("| Method | Path | Integrated | Source |")
        lines.append("|--------|------|-----------|--------|")
        for a in analysis["apis"]["endpoints"]:
            src = a.get("source", "").split("/")[-1]
            status = "✅" if a.get("integrated") else "⚠️ Mock"
            lines.append(f"| {a['method']} | `{a['path']}` | {status} | {src} |")
        lines.append("")

    if analysis["enums"]["definitions"]:
        lines.append("## Enums & Constants")
        lines.append("")
        for e in analysis["enums"]["definitions"]:
            lines.append(f"### {e['name']} ({e['type']})")
            if e["values"]:
                lines.append("| Key | Value |")
                lines.append("|-----|-------|")
                for k, v in e["values"].items():
                    lines.append(f"| {k} | {v} |")
            lines.append("")

    if analysis.get("models", {}).get("definitions"):
        lines.append("## Models / Entities")
        lines.append("")
        for m in analysis["models"]["definitions"]:
            lines.append(f"### {m['name']} ({m.get('framework', '')})")
            if m.get("fields"):
                lines.append("| Field | Type | Args |")
                lines.append("|-------|------|------|")
                for fld in m["fields"]:
                    lines.append(f"| {fld['name']} | {fld['type']} | {fld.get('args', '')} |")
            lines.append("")

    if proj.get("key_dependencies"):
        lines.append("## Key Dependencies")
        lines.append("")
        for dep, ver in sorted(proj["key_dependencies"].items()):
            lines.append(f"- `{dep}`: {ver}")
        lines.append("")

    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(
        description="Analyze any codebase (frontend, backend, fullstack) for PRD generation"
    )
    parser.add_argument("project", help="Path to project root")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    analysis = analyze_project(Path(args.project))

    if args.format == "markdown":
        output = format_markdown(analysis)
    else:
        output = json.dumps(analysis, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Written to {args.output}")
    else:
        print(output)
