# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_validator_base import *  # noqa: F403,E402
from skill_validator_p1 import ReportFormatter  # noqa: F401,E501


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate skill directories against quality standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python skill_validator.py engineering/my-skill
  python skill_validator.py engineering/my-skill --tier POWERFUL --json
  python skill_validator.py engineering/my-skill --verbose

Tier Options:
  BASIC     - Basic skill requirements (100+ lines SKILL.md, 1+ script)
  STANDARD  - Standard skill requirements (200+ lines, advanced features)
  POWERFUL  - Powerful skill requirements (300+ lines, comprehensive features)
        """
    )
    
    parser.add_argument("skill_path", 
                       help="Path to the skill directory to validate")
    parser.add_argument("--tier", 
                       choices=["BASIC", "STANDARD", "POWERFUL"],
                       help="Target tier for validation (optional)")
    parser.add_argument("--json", 
                       action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--verbose", 
                       action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        # Create validator and run validation
        validator = SkillValidator(args.skill_path, args.tier, args.verbose)
        report = validator.validate_skill_structure()
        
        # Format and output report
        if args.json:
            print(ReportFormatter.format_json(report))
        else:
            print(ReportFormatter.format_human_readable(report))
            
        # Exit with error code if validation failed
        if report.errors or report.overall_score < 60:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\nValidation interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Validation failed: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
