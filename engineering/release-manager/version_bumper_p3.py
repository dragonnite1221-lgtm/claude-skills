# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402


def _cscd_0(args, bump_type, bumper, output_data, recommended_version):
    if args.output_format == 'json':
        output_data = {
            'current_version': args.current_version,
            'recommended_version': recommended_version.to_string(),
            'recommended_version_with_v': recommended_version.to_string(include_v_prefix=True),
            'bump_type': bump_type.value,
            'prerelease': args.prerelease
        }
        
        if args.analysis:
            output_data['analysis'] = bumper.analyze_commits()
        
        if args.include_commands:
            output_data['commands'] = bumper.generate_bump_commands(recommended_version)
        
        if args.include_files:
            output_data['file_updates'] = bumper.generate_file_updates(recommended_version)
        
        output_text = json.dumps(output_data, indent=2)
    
    elif args.output_format == 'commands':
        commands = bumper.generate_bump_commands(recommended_version)
        output_lines = [
            f"# Version Bump Commands",
            f"# Current: {args.current_version}",
            f"# New: {recommended_version.to_string()}",
            f"# Bump Type: {bump_type.value}",
            ""
        ]
        
        for category, cmd_list in commands.items():
            output_lines.append(f"## {category.upper()}")
            for cmd in cmd_list:
                output_lines.append(cmd)
            output_lines.append("")
        
        output_text = '\n'.join(output_lines)
    
    else:  # text format
        output_lines = [
            f"Current Version: {args.current_version}",
            f"Recommended Version: {recommended_version.to_string()}",
            f"With v prefix: {recommended_version.to_string(include_v_prefix=True)}",
            f"Bump Type: {bump_type.value}",
            ""
        ]
        
        if args.analysis:
            analysis = bumper.analyze_commits()
            output_lines.extend([
                "Commit Analysis:",
                f"- Total commits: {analysis['total_commits']}",
                f"- Breaking changes: {len(analysis['breaking_changes'])}",
                f"- New features: {len(analysis['features'])}",
                f"- Bug fixes: {len(analysis['fixes'])}",
                f"- Ignored commits: {len(analysis['ignored'])}",
                ""
            ])
            
            if analysis['breaking_changes']:
                output_lines.append("Breaking Changes:")
                for change in analysis['breaking_changes']:
                    scope = f"({change['scope']})" if change['scope'] else ""
                    output_lines.append(f"  - {change['type']}{scope}: {change['description']}")
                output_lines.append("")
        
        if args.include_commands:
            commands = bumper.generate_bump_commands(recommended_version)
            output_lines.append("Bump Commands:")
            for category, cmd_list in commands.items():
                output_lines.append(f"  {category}:")
                for cmd in cmd_list:
                    if not cmd.startswith('#'):
                        output_lines.append(f"    {cmd}")
            output_lines.append("")
        
        output_text = '\n'.join(output_lines)
    return output_text
