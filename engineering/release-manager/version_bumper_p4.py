# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402
from version_bumper_p0 import BumpType, PreReleaseType  # noqa: F401,E501
from version_bumper_p3 import _cscd_0  # noqa: F401,E501


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Determine version bump based on conventional commits")
    parser.add_argument('--current-version', '-c', required=True,
                       help='Current version (e.g., 1.2.3, v1.2.3)')
    parser.add_argument('--input', '-i', type=str,
                       help='Input file with commits (default: stdin)')
    parser.add_argument('--input-format', choices=['git-log', 'json'], 
                       default='git-log', help='Input format')
    parser.add_argument('--prerelease', '-p', 
                       choices=['alpha', 'beta', 'rc'],
                       help='Generate pre-release version')
    parser.add_argument('--output-format', '-f', 
                       choices=['text', 'json', 'commands'], 
                       default='text', help='Output format')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file (default: stdout)')
    parser.add_argument('--include-commands', action='store_true',
                       help='Include bump commands in output')
    parser.add_argument('--include-files', action='store_true',
                       help='Include file update snippets')
    parser.add_argument('--custom-rules', type=str,
                       help='JSON string with custom type->bump rules')
    parser.add_argument('--ignore-types', type=str,
                       help='Comma-separated list of types to ignore')
    parser.add_argument('--analysis', '-a', action='store_true',
                       help='Include detailed commit analysis')
    
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
    
    # Initialize version bumper
    bumper = VersionBumper()
    
    try:
        bumper.set_current_version(args.current_version)
    except ValueError as e:
        print(f"Invalid current version: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Apply custom rules
    if args.custom_rules:
        try:
            custom_rules = json.loads(args.custom_rules)
            for commit_type, bump_type_str in custom_rules.items():
                bump_type = BumpType(bump_type_str.lower())
                bumper.add_custom_rule(commit_type, bump_type)
        except Exception as e:
            print(f"Invalid custom rules: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Set ignore types
    if args.ignore_types:
        bumper.ignore_types = [t.strip() for t in args.ignore_types.split(',')]
    
    # Parse commits
    try:
        if args.input_format == 'json':
            bumper.parse_commits_from_json(input_data)
        else:
            bumper.parse_commits_from_git_log(input_data)
    except Exception as e:
        print(f"Error parsing commits: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine pre-release type
    prerelease_type = None
    if args.prerelease:
        prerelease_type = PreReleaseType(args.prerelease)
    
    # Generate recommendation
    try:
        recommended_version = bumper.recommend_version(prerelease_type)
        bump_type = bumper.determine_bump_type()
    except Exception as e:
        print(f"Error determining version: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate output
    output_data = {}
    
    output_text = _cscd_0(args, bump_type, bumper, output_data, recommended_version)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
    else:
        print(output_text)
