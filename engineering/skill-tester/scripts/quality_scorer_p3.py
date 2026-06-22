# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p2 import QualityReportFormatter  # noqa: F401,E501


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Score skill quality across multiple dimensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quality_scorer.py engineering/my-skill
  python quality_scorer.py engineering/my-skill --detailed --json
  python quality_scorer.py engineering/my-skill --minimum-score 75
  python quality_scorer.py engineering/my-skill --include-security

Quality Dimensions (default: 4 dimensions × 25%):
  Documentation - SKILL.md quality, README, references, examples
  Code Quality   - Script complexity, error handling, structure, output
  Completeness   - Directory structure, assets, expected outputs, tests
  Usability      - Installation simplicity, usage clarity, help accessibility

With --include-security (5 dimensions × 20%):
  Security       - Sensitive data exposure, command injection, input validation

Letter Grades: A+ (95+), A (90+), A- (85+), B+ (80+), B (75+), B- (70+), C+ (65+), C (60+), C- (55+), D (50+), F (<50)
        """
    )
    
    parser.add_argument("skill_path",
                       help="Path to the skill directory to assess")
    parser.add_argument("--detailed",
                       action="store_true",
                       help="Show detailed component scores")
    parser.add_argument("--minimum-score",
                       type=float,
                       default=0,
                       help="Minimum acceptable score (exit with error if below)")
    parser.add_argument("--json",
                       action="store_true",
                       help="Output results in JSON format")
    parser.add_argument("--verbose",
                       action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--include-security",
                       action="store_true",
                       help="Include Security dimension (switches to 5 dimensions × 20%% each)")
                       
    args = parser.parse_args()
    
    try:
        # Create scorer and assess quality
        scorer = QualityScorer(args.skill_path, args.detailed, args.verbose, args.include_security)
        report = scorer.assess_quality()
        
        # Format and output report
        if args.json:
            print(QualityReportFormatter.format_json(report))
        else:
            print(QualityReportFormatter.format_human_readable(report, args.detailed))
            
        # Check minimum score requirement
        if report.overall_score < args.minimum_score:
            print(f"\nERROR: Quality score {report.overall_score:.1f} is below minimum {args.minimum_score}", file=sys.stderr)
            sys.exit(1)
            
        # Exit with different codes based on grade
        if report.letter_grade in ["A+", "A", "A-"]:
            sys.exit(0)  # Excellent
        elif report.letter_grade in ["B+", "B", "B-"]:
            sys.exit(0)  # Good
        elif report.letter_grade in ["C+", "C", "C-"]:
            sys.exit(0)  # Acceptable
        elif report.letter_grade == "D":
            sys.exit(2)  # Needs improvement
        else:  # F
            sys.exit(1)  # Poor quality
            
    except KeyboardInterrupt:
        print("\nQuality assessment interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Quality assessment failed: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
