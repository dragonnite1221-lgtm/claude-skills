# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Assess release readiness and generate release plans")
    parser.add_argument('--input', '-i', required=True,
                       help='Release plan JSON file')
    parser.add_argument('--output-format', '-f',
                       choices=['json', 'markdown', 'text'], 
                       default='text', help='Output format')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file (default: stdout)')
    parser.add_argument('--include-checklist', action='store_true',
                       help='Include release checklist in output')
    parser.add_argument('--include-communication', action='store_true', 
                       help='Include communication plan')
    parser.add_argument('--include-rollback', action='store_true',
                       help='Include rollback runbook')
    parser.add_argument('--min-coverage', type=float, default=80.0,
                       help='Minimum test coverage threshold')
    
    args = parser.parse_args()
    
    # Load release plan
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            plan_data = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize planner
    planner = ReleasePlanner()
    planner.min_test_coverage = args.min_coverage
    
    try:
        planner.load_release_plan(plan_data)
    except Exception as e:
        print(f"Error loading release plan: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate assessment
    assessment = planner.assess_release_readiness()
    
    # Generate optional components
    checklist = planner.generate_release_checklist() if args.include_checklist else None
    communication = planner.generate_communication_plan() if args.include_communication else None
    rollback = planner.generate_rollback_runbook() if args.include_rollback else None
    
    # Generate output
    if args.output_format == 'json':
        output_data = {
            'assessment': assessment,
            'checklist': checklist,
            'communication_plan': communication,
            'rollback_runbook': rollback
        }
        output_text = json.dumps(output_data, indent=2, default=str)
    
    elif args.output_format == 'markdown':
        output_lines = [
            f"# Release Readiness Report - {planner.release_name} v{planner.version}",
            "",
            f"**Overall Status:** {assessment['overall_status'].upper()}",
            f"**Readiness Score:** {assessment['readiness_score']:.1f}%",
            ""
        ]
        
        if assessment['blocking_issues']:
            output_lines.extend([
                "## 🚫 Blocking Issues",
                ""
            ])
            for issue in assessment['blocking_issues']:
                output_lines.append(f"- {issue}")
            output_lines.append("")
        
        if assessment['warnings']:
            output_lines.extend([
                "## ⚠️ Warnings",
                ""
            ])
            for warning in assessment['warnings']:
                output_lines.append(f"- {warning}")
            output_lines.append("")
        
        # Feature summary
        fs = assessment['feature_summary']
        output_lines.extend([
            "## Features Summary",
            "",
            f"- **Total:** {fs['total']}",
            f"- **Ready:** {fs['ready']}",
            f"- **In Progress:** {fs['in_progress']}",
            f"- **Blocked:** {fs['blocked']}",
            f"- **Breaking Changes:** {fs['breaking_changes']}",
            ""
        ])
        
        if checklist:
            output_lines.extend([
                "## Release Checklist",
                ""
            ])
            current_category = ""
            for item in checklist:
                if item['category'] != current_category:
                    current_category = item['category']
                    output_lines.append(f"### {current_category}")
                    output_lines.append("")
                
                status_icon = "✅" if item['status'] == 'ready' else "❌" if item['status'] == 'failed' else "⏳"
                output_lines.append(f"- {status_icon} {item['item']}")
            output_lines.append("")
        
        output_text = '\n'.join(output_lines)
    
    else:  # text format
        output_lines = [
            f"Release Readiness Report",
            f"========================",
            f"Release: {planner.release_name} v{planner.version}",
            f"Status: {assessment['overall_status'].upper()}",
            f"Readiness Score: {assessment['readiness_score']:.1f}%",
            ""
        ]
        
        if assessment['blocking_issues']:
            output_lines.extend(["BLOCKING ISSUES:", ""])
            for issue in assessment['blocking_issues']:
                output_lines.append(f"  ❌ {issue}")
            output_lines.append("")
        
        if assessment['warnings']:
            output_lines.extend(["WARNINGS:", ""])
            for warning in assessment['warnings']:
                output_lines.append(f"  ⚠️  {warning}")
            output_lines.append("")
        
        if assessment['recommendations']:
            output_lines.extend(["RECOMMENDATIONS:", ""])
            for rec in assessment['recommendations']:
                output_lines.append(f"  💡 {rec}")
            output_lines.append("")
        
        # Summary stats
        fs = assessment['feature_summary']
        gs = assessment['quality_gate_summary']
        
        output_lines.extend([
            f"FEATURE SUMMARY:",
            f"  Total: {fs['total']} | Ready: {fs['ready']} | Blocked: {fs['blocked']}",
            f"  Breaking Changes: {fs['breaking_changes']} | Missing Approvals: {fs['missing_approvals']}",
            "",
            f"QUALITY GATES:",
            f"  Total: {gs['total']} | Passed: {gs['passed']} | Failed: {gs['failed']}",
            ""
        ])
        
        output_text = '\n'.join(output_lines)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
    else:
        print(output_text)
