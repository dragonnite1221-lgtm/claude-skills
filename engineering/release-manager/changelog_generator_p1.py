# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from changelog_generator_base import *  # noqa: F403,E402


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(description="Generate changelog from conventional commits")
    parser.add_argument('--input', '-i', type=str, help='Input file (default: stdin)')
    parser.add_argument('--format', '-f', choices=['markdown', 'json', 'both'], 
                       default='markdown', help='Output format')
    parser.add_argument('--version', '-v', type=str, default='Unreleased',
                       help='Version for this release')
    parser.add_argument('--date', '-d', type=str, 
                       default=datetime.now().strftime("%Y-%m-%d"),
                       help='Release date (YYYY-MM-DD format)')
    parser.add_argument('--base-url', '-u', type=str, default='',
                       help='Base URL for commit links')
    parser.add_argument('--input-format', choices=['git-log', 'json'], 
                       default='git-log', help='Input format')
    parser.add_argument('--output', '-o', type=str, help='Output file (default: stdout)')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Include release summary statistics')
    
    args = parser.parse_args()
    
    # Read input
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_data = f.read()
    else:
        input_data = sys.stdin.read()
    
    if not input_data.strip():
        print("No input data provided", file=sys.stderr)
        sys.exit(1)
    
    # Initialize generator
    generator = ChangelogGenerator()
    generator.version = args.version
    generator.date = args.date
    generator.base_url = args.base_url
    
    # Parse input
    try:
        if args.input_format == 'json':
            generator.parse_json_commits(input_data)
        else:
            generator.parse_git_log_output(input_data)
    except Exception as e:
        print(f"Error parsing input: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not generator.commits:
        print("No valid commits found in input", file=sys.stderr)
        sys.exit(1)
    
    # Generate output
    output_lines = []
    
    if args.format in ['markdown', 'both']:
        changelog_md = generator.generate_markdown_changelog()
        if args.format == 'both':
            output_lines.append("# Markdown Changelog\n")
        output_lines.append(changelog_md)
    
    if args.format in ['json', 'both']:
        changelog_json = generator.generate_json_output()
        if args.format == 'both':
            output_lines.append("\n# JSON Output\n")
        output_lines.append(changelog_json)
    
    if args.summary:
        summary = generator.generate_release_summary()
        output_lines.append(f"\n# Release Summary")
        output_lines.append(f"- **Version:** {summary['version']}")
        output_lines.append(f"- **Total Commits:** {summary['total_commits']}")
        output_lines.append(f"- **Notable Changes:** {summary['notable_changes']}")
        output_lines.append(f"- **Breaking Changes:** {summary['breaking_changes']}")
        output_lines.append(f"- **Issue References:** {summary['issue_references']}")
        
        if summary['by_type']:
            output_lines.append("- **By Type:**")
            for commit_type, count in summary['by_type'].items():
                output_lines.append(f"  - {commit_type}: {count}")
    
    # Write output
    final_output = '\n'.join(output_lines)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(final_output)
    else:
        print(final_output)
