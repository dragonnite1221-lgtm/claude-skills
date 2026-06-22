# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fmea_analyzer_base import *  # noqa: F403,E402
# fmt: off
from fmea_analyzer_p1 import FMEAType  # noqa: E402,E501
from fmea_analyzer_p2 import FMEAAnalyzer  # noqa: E402,E501
from fmea_analyzer_p3 import format_fmea_text  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(description="FMEA Analyzer for Medical Device Risk Management")
    parser.add_argument("--type", choices=["design", "process"], default="design", help="FMEA type")
    parser.add_argument("--data", type=str, help="JSON file with FMEA data")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    fmea_type = FMEAType.DESIGN if args.type == "design" else FMEAType.PROCESS
    analyzer = FMEAAnalyzer(fmea_type)

    if args.data:
        with open(args.data) as f:
            data = json.load(f)
        report = analyzer.generate_report(
            product_process=data.get("product_process", ""),
            team=data.get("team", []),
            entries_data=data.get("entries", [])
        )
    else:
        # Demo data
        demo_entries = [
            {
                "item_process": "Battery Module",
                "function": "Provide power for 8 hours",
                "failure_mode": "Premature battery drain",
                "effect": "Device shuts down during procedure",
                "severity": 8,
                "cause": "Cell degradation due to temperature cycling",
                "occurrence": 4,
                "current_controls": "Incoming battery testing, temperature spec in IFU",
                "detection": 5,
                "recommended_actions": ["Add battery health monitoring algorithm", "Implement low-battery warning at 20%"]
            },
            {
                "item_process": "Software Controller",
                "function": "Control device operation",
                "failure_mode": "Firmware crash",
                "effect": "Device becomes unresponsive",
                "severity": 7,
                "cause": "Memory leak in logging module",
                "occurrence": 3,
                "current_controls": "Code review, unit testing, integration testing",
                "detection": 4,
                "recommended_actions": ["Add watchdog timer", "Implement memory usage monitoring"]
            },
            {
                "item_process": "Sterile Packaging",
                "function": "Maintain sterility until use",
                "failure_mode": "Seal breach",
                "effect": "Device contamination",
                "severity": 9,
                "cause": "Sealing jaw temperature variation",
                "occurrence": 2,
                "current_controls": "Seal integrity testing (dye penetration), SPC on sealing process",
                "detection": 3,
                "recommended_actions": ["Add real-time seal temperature monitoring", "Implement 100% seal integrity testing"]
            }
        ]
        report = analyzer.generate_report(
            product_process="Insulin Pump Model X200",
            team=["Quality Engineer", "R&D Lead", "Manufacturing Engineer", "Risk Manager"],
            entries_data=demo_entries
        )

    if args.output == "json":
        result = {
            "fmea_type": report.fmea_type,
            "product_process": report.product_process,
            "date": report.date,
            "team": report.team,
            "entries": [asdict(e) for e in report.entries],
            "summary": report.summary,
            "risk_reduction_actions": report.risk_reduction_actions
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_fmea_text(report))
