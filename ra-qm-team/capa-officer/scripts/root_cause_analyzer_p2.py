# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from root_cause_analyzer_base import *  # noqa: F403,E402
from root_cause_analyzer_p1 import format_rca_text  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Root Cause Analyzer for CAPA Investigations")
    parser.add_argument("--problem", type=str, help="Problem statement")
    parser.add_argument("--method", choices=["5why", "fishbone", "fault-tree", "kt"],
                       default="5why", help="Analysis method")
    parser.add_argument("--data", type=str, help="JSON file with analysis data")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    analyzer = RootCauseAnalyzer()

    if args.data:
        with open(args.data) as f:
            data = json.load(f)
        problem = data.get("problem", "Unknown problem")
        method = data.get("method", "5-Why")
        rca = analyzer.full_analysis(problem, method, data)
    elif args.problem:
        method_map = {"5why": "5-Why", "fishbone": "Fishbone", "fault-tree": "Fault Tree", "kt": "Kepner-Tregoe"}
        rca = analyzer.full_analysis(args.problem, method_map.get(args.method, "5-Why"))
    else:
        # Demo
        demo_data = {
            "method": "5-Why",
            "whys": [
                {"question": "Why did the product fail inspection?", "answer": "Surface defect detected on 15% of units", "evidence": "QC inspection records"},
                {"question": "Why did surface defects occur?", "answer": "Injection molding temperature was outside spec", "evidence": "Process monitoring data"},
                {"question": "Why was temperature outside spec?", "answer": "Temperature controller calibration drift", "evidence": "Calibration log"},
                {"question": "Why did calibration drift go undetected?", "answer": "No automated alert for drift, manual checks missed it", "evidence": "SOP review"},
                {"question": "Why was there no automated alert?", "answer": "Process monitoring system lacks drift detection capability - systemic gap", "evidence": "System requirements review"}
            ]
        }
        rca = analyzer.full_analysis("High defect rate in injection molding process", "5-Why", demo_data)

    if args.output == "json":
        result = {
            "investigation_id": rca.investigation_id,
            "problem": rca.problem_statement,
            "method": rca.analysis_method,
            "root_causes": [asdict(rc) for rc in rca.root_causes],
            "recommendations": [asdict(rec) for rec in rca.recommendations],
            "analysis_details": rca.analysis_details,
            "confidence": rca.confidence_level
        }
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_rca_text(rca))
