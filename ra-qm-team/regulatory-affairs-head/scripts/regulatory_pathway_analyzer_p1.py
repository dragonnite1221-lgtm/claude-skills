# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402
from regulatory_pathway_analyzer_p0 import DeviceProfile, PathwayAnalysis  # noqa: F401,E501


def format_analysis_text(analysis: PathwayAnalysis) -> str:
    """Format analysis as readable text report."""
    lines = [
        "=" * 70,
        "REGULATORY PATHWAY ANALYSIS REPORT",
        "=" * 70,
        f"Device: {analysis.device.device_name}",
        f"Intended Use: {analysis.device.intended_use}",
        f"Device Class: {analysis.device.device_class}",
        f"Target Markets: {', '.join(analysis.device.target_markets)}",
        "",
        "DEVICE CHARACTERISTICS",
        "-" * 40,
        f"  Novel Technology: {'Yes' if analysis.device.novel_technology else 'No'}",
        f"  Predicate Available: {'Yes' if analysis.device.predicate_available else 'No'}",
        f"  Implantable: {'Yes' if analysis.device.implantable else 'No'}",
        f"  Life-Sustaining: {'Yes' if analysis.device.life_sustaining else 'No'}",
        f"  Software/AI Component: {'Yes' if analysis.device.software_component or analysis.device.ai_ml_component else 'No'}",
        f"  Sterile: {'Yes' if analysis.device.sterile else 'No'}",
        "",
        "RECOMMENDED PATHWAYS",
        "-" * 40,
    ]

    for pathway in analysis.recommended_pathways:
        lines.extend([
            "",
            f"  [{pathway.market}] {pathway.pathway_name}",
            f"  Recommendation: {pathway.recommendation_level}",
            f"  Timeline: {pathway.estimated_timeline_months[0]}-{pathway.estimated_timeline_months[1]} months",
            f"  Estimated Cost: ${pathway.estimated_cost_usd[0]:,} - ${pathway.estimated_cost_usd[1]:,}",
            f"  Key Requirements:",
        ])
        for req in pathway.key_requirements:
            lines.append(f"    • {req}")
        lines.append(f"  Advantages:")
        for adv in pathway.advantages:
            lines.append(f"    + {adv}")
        lines.append(f"  Risks:")
        for risk in pathway.risks:
            lines.append(f"    ! {risk}")

    lines.extend([
        "",
        "OPTIMAL SUBMISSION SEQUENCE",
        "-" * 40,
    ])
    for step in analysis.optimal_sequence:
        lines.append(f"  {step}")

    lines.extend([
        "",
        "TOTAL ESTIMATES",
        "-" * 40,
        f"  Combined Timeline: {analysis.total_timeline_months[0]}-{analysis.total_timeline_months[1]} months",
        f"  Combined Cost: ${analysis.total_estimated_cost[0]:,} - ${analysis.total_estimated_cost[1]:,}",
        "",
        "CRITICAL SUCCESS FACTORS",
        "-" * 40,
    ])
    for i, factor in enumerate(analysis.critical_success_factors, 1):
        lines.append(f"  {i}. {factor}")

    if analysis.warnings:
        lines.extend([
            "",
            "WARNINGS",
            "-" * 40,
        ])
        for warning in analysis.warnings:
            lines.append(f"  ⚠ {warning}")

    lines.append("=" * 70)
    return "\n".join(lines)


def interactive_mode():
    """Interactive device profiling."""
    print("=" * 60)
    print("Regulatory Pathway Analyzer - Interactive Mode")
    print("=" * 60)

    device = DeviceProfile(
        device_name=input("\nDevice Name: ").strip(),
        intended_use=input("Intended Use: ").strip(),
        device_class=input("Device Class (I/IIa/IIb/III): ").strip(),
        novel_technology=input("Novel technology? (y/n): ").strip().lower() == 'y',
        predicate_available=input("Predicate device available? (y/n): ").strip().lower() == 'y',
        implantable=input("Implantable? (y/n): ").strip().lower() == 'y',
        life_sustaining=input("Life-sustaining? (y/n): ").strip().lower() == 'y',
        software_component=input("Software component? (y/n): ").strip().lower() == 'y',
        ai_ml_component=input("AI/ML component? (y/n): ").strip().lower() == 'y',
    )

    markets = input("Target markets (comma-separated, e.g., US-FDA,EU-MDR): ").strip()
    if markets:
        device.target_markets = [m.strip() for m in markets.split(",")]

    analyzer = RegulatoryPathwayAnalyzer()
    analysis = analyzer.analyze(device)
    print("\n" + format_analysis_text(analysis))
