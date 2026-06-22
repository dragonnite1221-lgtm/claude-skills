# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_modeler_base import *  # noqa: F403,E402
# fmt: off
from threat_modeler_p1 import STRIDECategory, Threat  # noqa: E402,E501
from threat_modeler_p4 import THREAT_DATABASE, get_threats_for_component  # noqa: E402,E501
# fmt: on


def calculate_dread_score(threat: Threat) -> Dict:
    """Calculate DREAD score for a threat."""
    # Map threat properties to DREAD factors
    damage = threat.severity * 2
    reproducibility = 8 if threat.likelihood >= 4 else (5 if threat.likelihood >= 2 else 3)
    exploitability = threat.likelihood * 2
    affected_users = 8 if "mass" in threat.impact.lower() or "full" in threat.impact.lower() else 5
    discoverability = 7 if threat.likelihood >= 3 else 4

    dread = {
        "damage": min(damage, 10),
        "reproducibility": reproducibility,
        "exploitability": min(exploitability, 10),
        "affected_users": affected_users,
        "discoverability": discoverability
    }
    dread["total"] = sum(dread.values()) / 5
    return dread
def format_threat_report(component: str, threats: List[Threat]) -> str:
    """Format threats as a readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"THREAT MODEL: {component.upper()}")
    lines.append("=" * 70)
    lines.append("")

    # Summary
    critical = sum(1 for t in threats if t.risk_level == "Critical")
    high = sum(1 for t in threats if t.risk_level == "High")
    medium = sum(1 for t in threats if t.risk_level == "Medium")
    low = sum(1 for t in threats if t.risk_level == "Low")

    lines.append("SUMMARY:")
    lines.append(f"  Total Threats: {len(threats)}")
    lines.append(f"  Critical: {critical} | High: {high} | Medium: {medium} | Low: {low}")
    lines.append("")

    # Threats by STRIDE category
    for stride in STRIDECategory:
        category_threats = [t for t in threats if t.category == stride.value]
        if category_threats:
            lines.append("-" * 70)
            lines.append(f"[{stride.value.upper()}]")
            lines.append("-" * 70)

            for threat in category_threats:
                dread = calculate_dread_score(threat)
                lines.append("")
                lines.append(f"  {threat.name}")
                lines.append(f"  Risk: {threat.risk_level} (Score: {threat.risk_score}/25)")
                lines.append(f"  DREAD: {dread['total']:.1f}/10")
                lines.append(f"  Description: {threat.description}")
                lines.append(f"  Attack Vector: {threat.attack_vector}")
                lines.append(f"  Impact: {threat.impact}")
                lines.append("  Mitigations:")
                for m in threat.mitigations:
                    lines.append(f"    - {m}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)
def format_json_report(component: str, threats: List[Threat]) -> Dict:
    """Format threats as JSON structure."""
    return {
        "component": component,
        "analysis_date": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_threats": len(threats),
            "by_risk_level": {
                "critical": sum(1 for t in threats if t.risk_level == "Critical"),
                "high": sum(1 for t in threats if t.risk_level == "High"),
                "medium": sum(1 for t in threats if t.risk_level == "Medium"),
                "low": sum(1 for t in threats if t.risk_level == "Low")
            }
        },
        "threats": [
            {
                "category": t.category,
                "name": t.name,
                "description": t.description,
                "attack_vector": t.attack_vector,
                "impact": t.impact,
                "likelihood": t.likelihood,
                "severity": t.severity,
                "risk_score": t.risk_score,
                "risk_level": t.risk_level,
                "dread": calculate_dread_score(t),
                "mitigations": t.mitigations
            }
            for t in threats
        ]
    }
def interactive_mode():
    """Run interactive threat modeling session."""
    print("\n" + "=" * 50)
    print("STRIDE THREAT MODELER - Interactive Mode")
    print("=" * 50)

    component = input("\nEnter component name (e.g., 'User Authentication'): ").strip()
    if not component:
        print("Component name required.")
        return

    threats = get_threats_for_component(component)

    if not threats:
        print(f"No threats found for component: {component}")
        return

    print(format_threat_report(component, threats))
def list_all_threats():
    """List all threats in the database."""
    print("\n" + "=" * 50)
    print("THREAT DATABASE")
    print("=" * 50)

    for category, threats in THREAT_DATABASE.items():
        print(f"\n[{category.upper()}]")
        for threat in threats:
            print(f"  - {threat.category}: {threat.name} (Risk: {threat.risk_level})")
