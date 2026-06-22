# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chart_analyzer_base import *  # noqa: F403,E402
# fmt: off
from chart_analyzer_p1 import DEMO_CHART_YAML  # noqa: E402,E501
from chart_analyzer_p2 import DEMO_DEPLOYMENT, DEMO_VALUES_YAML  # noqa: E402,E501
from chart_analyzer_p5 import analyze_chart  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="helm-chart-builder: Helm chart static analyzer"
    )
    parser.add_argument("chartdir", nargs="?", help="Path to Helm chart directory (omit for demo)")
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Security-focused analysis only",
    )
    args = parser.parse_args()

    if args.chartdir:
        chart_dir = Path(args.chartdir)
        if not chart_dir.is_dir():
            print(f"Error: Not a directory: {args.chartdir}", file=sys.stderr)
            sys.exit(1)
        analyze_chart(chart_dir, args.output, args.security)
    else:
        print("No chart directory provided. Running demo analysis...\n")
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            chart_dir = Path(tmpdir) / "demo-app"
            chart_dir.mkdir()
            (chart_dir / "Chart.yaml").write_text(DEMO_CHART_YAML)
            (chart_dir / "values.yaml").write_text(DEMO_VALUES_YAML)
            templates_dir = chart_dir / "templates"
            templates_dir.mkdir()
            (templates_dir / "deployment.yaml").write_text(DEMO_DEPLOYMENT)
            analyze_chart(chart_dir, args.output, args.security)
