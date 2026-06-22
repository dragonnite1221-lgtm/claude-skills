# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p1 import TestReportFormatter  # noqa: F401,E501


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test Python scripts in a skill directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script_tester.py engineering/my-skill
  python script_tester.py engineering/my-skill --timeout 60 --json
  python script_tester.py engineering/my-skill --verbose

Test Categories:
  - Syntax validation (AST parsing)
  - Import validation (stdlib only)
  - Argparse implementation
  - Main guard presence
  - Basic execution testing
  - Help functionality
  - Sample data processing
  - Output format compliance
        """
    )
    
    parser.add_argument("skill_path",
                       help="Path to the skill directory containing scripts to test")
    parser.add_argument("--timeout",
                       type=int,
                       default=30,
                       help="Timeout for script execution tests in seconds (default: 30)")
    parser.add_argument("--json",
                       action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--verbose",
                       action="store_true", 
                       help="Enable verbose logging")
                       
    args = parser.parse_args()
    
    try:
        # Create tester and run tests
        tester = ScriptTester(args.skill_path, args.timeout, args.verbose)
        test_suite = tester.test_all_scripts()
        
        # Format and output results
        if args.json:
            print(TestReportFormatter.format_json(test_suite))
        else:
            print(TestReportFormatter.format_human_readable(test_suite))
            
        # Exit with appropriate code
        if test_suite.global_errors:
            sys.exit(1)
        elif test_suite.summary.get("overall_status") == "FAIL":
            sys.exit(1)
        elif test_suite.summary.get("overall_status") == "PARTIAL":
            sys.exit(2)  # Partial success
        else:
            sys.exit(0)  # Success
            
    except KeyboardInterrupt:
        print("\nTesting interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Testing failed: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
