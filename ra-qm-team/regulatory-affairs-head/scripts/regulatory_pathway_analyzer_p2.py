# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402
from regulatory_pathway_analyzer_p0 import DeviceProfile  # noqa: F401,E501
from regulatory_pathway_analyzer_p1 import format_analysis_text, interactive_mode  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Regulatory Pathway Analyzer for Medical Devices")
    parser.add_argument("--device-name", type=str, help="Device name")
    parser.add_argument("--device-class", type=str, choices=["I", "IIa", "IIb", "III"], help="Device classification")
    parser.add_argument("--predicate", type=str, choices=["yes", "no"], help="Predicate device available")
    parser.add_argument("--novel", action="store_true", help="Novel technology")
    parser.add_argument("--implantable", action="store_true", help="Implantable device")
    parser.add_argument("--software", action="store_true", help="Software component")
    parser.add_argument("--ai-ml", action="store_true", help="AI/ML component")
    parser.add_argument("--market", type=str, default="all", help="Target market(s)")
    parser.add_argument("--data", type=str, help="JSON file with device profile")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.data:
        with open(args.data) as f:
            data = json.load(f)
        device = DeviceProfile(**data)
    elif args.device_class:
        device = DeviceProfile(
            device_name=args.device_name or "Unnamed Device",
            intended_use="Medical device",
            device_class=args.device_class,
            novel_technology=args.novel,
            predicate_available=args.predicate == "yes" if args.predicate else True,
            implantable=args.implantable,
            software_component=args.software,
            ai_ml_component=args.ai_ml,
        )
        if args.market != "all":
            device.target_markets = [m.strip() for m in args.market.split(",")]
    else:
        # Demo mode
        device = DeviceProfile(
            device_name="SmartGlucose Monitor Pro",
            intended_use="Continuous glucose monitoring for diabetes management",
            device_class="II",
            novel_technology=False,
            predicate_available=True,
            software_component=True,
            ai_ml_component=True,
            target_markets=["US-FDA", "EU-MDR"]
        )

    analyzer = RegulatoryPathwayAnalyzer()
    analysis = analyzer.analyze(device)

    if args.output == "json":
        result = {
            "device": asdict(analysis.device),
            "pathways": [asdict(p) for p in analysis.recommended_pathways],
            "optimal_sequence": analysis.optimal_sequence,
            "total_timeline_months": list(analysis.total_timeline_months),
            "total_estimated_cost": list(analysis.total_estimated_cost),
            "critical_success_factors": analysis.critical_success_factors,
            "warnings": analysis.warnings
        }
        print(json.dumps(result, indent=2))
    else:
        print(format_analysis_text(analysis))
