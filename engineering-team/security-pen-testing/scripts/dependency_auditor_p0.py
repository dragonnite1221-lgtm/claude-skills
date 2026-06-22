# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_auditor_base import *  # noqa: F403,E402


@dataclass
class Dependency:
    """Represents a parsed dependency."""
    name: str
    version: str
    ecosystem: str  # npm, pypi, go, rubygems
    is_dev: bool = False


@dataclass
class VulnerabilityFinding:
    """A known vulnerability match for a dependency."""
    package: str
    installed_version: str
    vulnerable_range: str
    cve_id: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    remediation: str
    cvss_score: float = 0.0
    references: List[str] = field(default_factory=list)


@dataclass
class RiskyPattern:
    """A risky dependency pattern (not a CVE, but a concern)."""
    package: str
    pattern_type: str  # pinning, wildcard, deprecated, typosquat
    severity: str
    description: str
    recommendation: str


def format_report_text(result: Dict) -> str:
    """Format audit result as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("DEPENDENCY VULNERABILITY AUDIT REPORT")
    lines.append(f"Manifest: {result['manifest']}")
    lines.append(f"Ecosystem: {result['ecosystem']}")
    lines.append(f"Total dependencies: {result['total_dependencies']} ({result['dev_dependencies']} dev)")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    summary = result["summary"]
    lines.append(f"\nSummary: {summary['critical']} critical, {summary['high']} high, "
                 f"{summary['medium']} medium, {summary['low']} low, "
                 f"{summary['risky_patterns_count']} risky pattern(s)")

    vulns = result["vulnerability_findings"]
    if vulns:
        lines.append(f"\n--- VULNERABILITY FINDINGS ({len(vulns)}) ---\n")
        for v in vulns:
            lines.append(f"  [{v.severity.upper()}] {v.package} {v.installed_version}")
            lines.append(f"    CVE: {v.cve_id} (CVSS: {v.cvss_score})")
            lines.append(f"    {v.title}")
            lines.append(f"    Vulnerable: {v.vulnerable_range}")
            lines.append(f"    Fix: {v.remediation}")
            lines.append("")
    else:
        lines.append("\nNo known vulnerabilities found in dependencies.")

    risky = result["risky_patterns"]
    if risky:
        lines.append(f"\n--- RISKY PATTERNS ({len(risky)}) ---\n")
        for r in risky:
            lines.append(f"  [{r.severity.upper()}] {r.package} — {r.pattern_type}")
            lines.append(f"    {r.description}")
            lines.append(f"    Fix: {r.recommendation}")
            lines.append("")

    return "\n".join(lines)
