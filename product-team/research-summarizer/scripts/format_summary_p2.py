# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from format_summary_base import *  # noqa: F403,E402
# fmt: off
from format_summary_p1 import LENGTH_CONFIGS, TEMPLATES  # noqa: E402,E501
# fmt: on


def render_template(template_key, length="standard", output_format="text"):
    """Render a summary template."""
    template = TEMPLATES[template_key]
    sections = template["sections"]

    if length == "brief":
        # Keep only first 4 sections for brief output
        sections = sections[:4]

    if output_format == "json":
        result = {
            "template": template_key,
            "name": template["name"],
            "description": template["description"],
            "length": length,
            "generated": datetime.now().strftime("%Y-%m-%d"),
            "sections": [],
        }
        for title, content in sections:
            result["sections"].append({
                "heading": title,
                "placeholder": content,
            })
        return json.dumps(result, indent=2)

    # Text/Markdown output
    lines = []
    lines.append(f"# {template['name']}")
    lines.append(f"_{template['description']}_\n")
    lines.append(f"Length: {LENGTH_CONFIGS[length]['label']}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n")
    lines.append("---\n")

    for title, content in sections:
        lines.append(f"## {title}\n")
        # Indent content for readability
        for line in content.split("\n"):
            lines.append(line)
        lines.append("")

    lines.append("---")
    lines.append("_Template from research-summarizer skill_")

    return "\n".join(lines)
def list_templates(output_format="text"):
    """List all available templates."""
    if output_format == "json":
        result = []
        for key, tmpl in TEMPLATES.items():
            result.append({
                "key": key,
                "name": tmpl["name"],
                "description": tmpl["description"],
                "sections": len(tmpl["sections"]),
            })
        return json.dumps(result, indent=2)

    lines = []
    lines.append("Available Summary Templates\n")
    lines.append(f"{'KEY':<15} {'NAME':<30} {'SECTIONS':>8}  DESCRIPTION")
    lines.append(f"{'─' * 90}")
    for key, tmpl in TEMPLATES.items():
        lines.append(
            f"{key:<15} {tmpl['name']:<30} {len(tmpl['sections']):>8}  {tmpl['description'][:40]}"
        )
    return "\n".join(lines)
def main():
    parser = argparse.ArgumentParser(
        description="research-summarizer: Generate structured summary templates"
    )
    parser.add_argument(
        "--template", "-t",
        choices=list(TEMPLATES.keys()),
        help="Template type to generate",
    )
    parser.add_argument(
        "--length", "-l",
        choices=["brief", "standard", "detailed"],
        default="standard",
        help="Output length (default: standard)",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List all available templates",
    )
    args = parser.parse_args()

    if args.list_templates:
        print(list_templates(args.output))
        return

    if not args.template:
        print("No template specified. Available templates:\n")
        print(list_templates(args.output))
        print("\nUsage: python scripts/format_summary.py --template academic")
        return

    print(render_template(args.template, args.length, args.output))
