# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_tracker_base import *  # noqa: F403,E402
# fmt: off
from compliance_tracker_p1 import FRAMEWORKS  # noqa: E402,E501
from compliance_tracker_p4 import load_control_library  # noqa: E402,E501
from compliance_tracker_p5 import calculate_framework_coverage, print_control_table, print_framework_summary, print_gap_analysis, print_header  # noqa: E402,E501
from compliance_tracker_p6 import export_csv, print_framework_profiles, print_high_leverage, print_roadmap  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="CISO Compliance Tracker — Multi-framework coverage and roadmap"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--csv", metavar="FILE", help="Export CSV to file")
    parser.add_argument(
        "--framework", metavar="FRAMEWORK",
        choices=list(FRAMEWORKS.keys()),
        help="Filter to single framework (soc2, iso27001, hipaa, gdpr)"
    )
    parser.add_argument("--gap-analysis", action="store_true", help="Show gap analysis")
    parser.add_argument("--roadmap", metavar="FRAMEWORKS",
                        help="Sequenced roadmap for frameworks e.g. 'soc2,iso27001'")
    parser.add_argument("--profiles", action="store_true", help="Show framework profiles")
    parser.add_argument("--leverage", action="store_true", help="Show high-leverage controls")
    args = parser.parse_args()

    controls = load_control_library()
    coverage = calculate_framework_coverage(controls)

    if args.json:
        output = {
            "generated": datetime.now().isoformat(),
            "frameworks": FRAMEWORKS,
            "coverage": coverage,
            "controls": controls,
        }
        print(json.dumps(output, indent=2, default=str))
        return

    if args.csv:
        export_csv(controls, args.csv)
        return

    print_header()

    if args.profiles:
        print_framework_profiles()
        return

    if args.roadmap:
        target_fws = [fw.strip() for fw in args.roadmap.split(",") if fw.strip() in FRAMEWORKS]
        if not target_fws:
            print(f"Unknown frameworks. Valid: {', '.join(FRAMEWORKS.keys())}")
            sys.exit(1)
        print_framework_summary(coverage)
        print_roadmap(controls, target_fws)
        return

    print_framework_summary(coverage)
    print_control_table(controls, args.framework)

    if args.gap_analysis:
        print_gap_analysis(coverage)

    if args.leverage:
        print_high_leverage(controls)

    if not any([args.framework, args.gap_analysis, args.leverage]):
        print_high_leverage(controls)
        print_gap_analysis(coverage)

    print("\n💡 NEXT STEPS")
    print("  --roadmap soc2,iso27001     Priority order for dual-framework")
    print("  --framework hipaa           HIPAA-only control view")
    print("  --gap-analysis              What's not started")
    print("  --leverage                  Controls covering most frameworks")
    print("  --profiles                  Framework timelines and costs")
    print("  --csv controls.csv          Export for stakeholder review")
    print()
