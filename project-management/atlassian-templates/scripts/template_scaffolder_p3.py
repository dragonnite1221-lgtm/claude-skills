# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from template_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from template_scaffolder_p2 import TEMPLATE_REGISTRY, build_custom_template, format_json_output, format_text_output  # noqa: E402,E501
# fmt: on


def format_list_output(output_format: str) -> str:
    """Format available templates list."""
    if output_format == "json":
        templates = {}
        for name, func in TEMPLATE_REGISTRY.items():
            result = func()
            templates[name] = {
                "name": result["name"],
                "labels": result["labels"],
            }
        return json.dumps(templates, indent=2)

    lines = []
    lines.append("=" * 60)
    lines.append("AVAILABLE TEMPLATES")
    lines.append("=" * 60)
    lines.append("")
    for name, func in TEMPLATE_REGISTRY.items():
        result = func()
        lines.append(f"  {name}")
        lines.append(f"    Name: {result['name']}")
        lines.append(f"    Labels: {', '.join(result['labels'])}")
        lines.append("")
    lines.append(f"Total templates: {len(TEMPLATE_REGISTRY)}")
    lines.append("")
    lines.append("Usage:")
    lines.append("  python template_scaffolder.py <template-name>")
    lines.append('  python template_scaffolder.py custom --sections "Section1,Section2" --macros toc,status')
    return "\n".join(lines)
def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Confluence page template markup"
    )
    parser.add_argument(
        "template",
        nargs="?",
        help="Template name or 'custom' for custom template",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available template types",
    )
    parser.add_argument(
        "--sections",
        help='Comma-separated section names for custom template (e.g., "Overview,Goals,Action Items")',
    )
    parser.add_argument(
        "--macros",
        help='Comma-separated macro names to include (e.g., "toc,status,info")',
    )

    args = parser.parse_args()

    try:
        if args.list:
            print(format_list_output(args.format))
            return 0

        if not args.template:
            parser.error("template name is required unless --list is used")

        template_name = args.template.lower()

        if template_name == "custom":
            if not args.sections:
                parser.error("--sections is required for custom templates")
            sections = [s.strip() for s in args.sections.split(",")]
            macros = [m.strip() for m in args.macros.split(",")] if args.macros else []
            result = build_custom_template(sections, macros)
        elif template_name in TEMPLATE_REGISTRY:
            result = TEMPLATE_REGISTRY[template_name]()
        else:
            available = ", ".join(sorted(TEMPLATE_REGISTRY.keys()))
            print(f"Error: Unknown template '{template_name}'. Available: {available}", file=sys.stderr)
            return 1

        if args.format == "json":
            print(json.dumps(format_json_output(result), indent=2))
        else:
            print(format_text_output(result))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
