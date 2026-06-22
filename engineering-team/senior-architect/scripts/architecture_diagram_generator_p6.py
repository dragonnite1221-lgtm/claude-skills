# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_diagram_generator_base import *  # noqa: F403,E402
# fmt: off
from architecture_diagram_generator_p1 import ProjectScanner  # noqa: E402,E501
from architecture_diagram_generator_p3 import MermaidGenerator  # noqa: E402,E501
from architecture_diagram_generator_p4 import PlantUMLGenerator  # noqa: E402,E501
from architecture_diagram_generator_p5 import ASCIIGenerator  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description='Generate architecture diagrams from project structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s ./my-project --format mermaid
  %(prog)s ./my-project --format plantuml --type layer
  %(prog)s ./my-project --format ascii -o architecture.txt

Diagram types:
  component   - Shows modules and their relationships (default)
  layer       - Shows architectural layers
  deployment  - Shows deployment topology

Output formats:
  mermaid     - Mermaid.js format (default)
  plantuml    - PlantUML format
  ascii       - ASCII art format
        '''
    )

    parser.add_argument(
        'project_path',
        help='Path to the project directory'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['mermaid', 'plantuml', 'ascii'],
        default='mermaid',
        help='Output format (default: mermaid)'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['component', 'layer', 'deployment'],
        default='component',
        help='Diagram type (default: component)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path (prints to stdout if not specified)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw scan results as JSON'
    )

    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)

    if not project_path.is_dir():
        print(f"Error: Project path is not a directory: {project_path}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Scanning project: {project_path}")

    # Scan project
    scanner = ProjectScanner(project_path)
    scan_result = scanner.scan()

    if args.verbose:
        print(f"Found {len(scan_result['components'])} components")
        print(f"Found {len(scan_result['relationships'])} relationships")
        print(f"Technologies: {', '.join(scan_result['technologies']) or 'none detected'}")

    # Output raw JSON if requested
    if args.json:
        output = json.dumps(scan_result, indent=2)
        if args.output:
            Path(args.output).write_text(output)
            print(f"Results written to {args.output}")
        else:
            print(output)
        return

    # Generate diagram
    generators = {
        'mermaid': MermaidGenerator,
        'plantuml': PlantUMLGenerator,
        'ascii': ASCIIGenerator,
    }

    generator = generators[args.format](scan_result)
    diagram = generator.generate(args.type)

    # Output
    if args.output:
        Path(args.output).write_text(diagram)
        print(f"Diagram written to {args.output}")
    else:
        print(diagram)
