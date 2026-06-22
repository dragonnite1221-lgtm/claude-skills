# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_auditor_base import *  # noqa: F403,E402
from dependency_auditor_p0 import Dependency, RiskyPattern, VulnerabilityFinding  # noqa: F401,E501


class DependencyAuditorMixin1:
    def _parse_gemfile(self, content: str) -> List[Dependency]:
        """Parse Ruby Gemfile."""
        deps = []
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r'''gem\s+['"]([\w-]+)['"](?:\s*,\s*['"]([^'"]*)['"'])?''', line)
            if match:
                name = match.group(1)
                version = match.group(2) or "unknown"
                version = re.sub(r"[~><=\s]", "", version)
                deps.append(Dependency(name=name, version=version, ecosystem="rubygems"))
        return deps
    @staticmethod
    def _version_below(installed: str, threshold: str) -> bool:
        """Check if installed version is below threshold (simple numeric comparison)."""
        try:
            inst_parts = [int(x) for x in installed.split(".") if x.isdigit()]
            thresh_parts = [int(x) for x in threshold.split(".") if x.isdigit()]
            # Pad shorter list
            max_len = max(len(inst_parts), len(thresh_parts))
            inst_parts.extend([0] * (max_len - len(inst_parts)))
            thresh_parts.extend([0] * (max_len - len(thresh_parts)))
            return inst_parts < thresh_parts
        except (ValueError, IndexError):
            return False
    def _check_vulnerabilities(self, deps: List[Dependency]) -> List[VulnerabilityFinding]:
        """Check dependencies against known CVE database."""
        findings = []
        for dep in deps:
            for vuln in self.KNOWN_VULNS:
                if (dep.ecosystem == vuln["ecosystem"] and
                        dep.name.lower() == vuln["package"].lower() and
                        self._version_below(dep.version, vuln["below"])):
                    findings.append(VulnerabilityFinding(
                        package=dep.name,
                        installed_version=dep.version,
                        vulnerable_range=f"< {vuln['below']}",
                        cve_id=vuln["cve"],
                        severity=vuln["severity"],
                        title=vuln["title"],
                        description=vuln["description"],
                        remediation=vuln["remediation"],
                        cvss_score=vuln.get("cvss", 0.0),
                        references=[f"https://nvd.nist.gov/vuln/detail/{vuln['cve']}"],
                    ))
        return findings
    def _check_risky_patterns(self, deps: List[Dependency]) -> List[RiskyPattern]:
        """Detect risky dependency patterns."""
        patterns = []
        ecosystem = deps[0].ecosystem if deps else "unknown"

        # Check for typosquat packages
        typosquats = self.TYPOSQUAT_PACKAGES.get(ecosystem, [])
        for dep in deps:
            if dep.name.lower() in [t.lower() for t in typosquats]:
                patterns.append(RiskyPattern(
                    package=dep.name,
                    pattern_type="typosquat",
                    severity="critical",
                    description=f"'{dep.name}' is a known typosquat or malicious package name.",
                    recommendation="Remove immediately and check for compromised data. Install the legitimate package.",
                ))

        # Check for wildcard/unpinned versions
        for dep in deps:
            if dep.version in ("*", "latest", "unknown", ""):
                patterns.append(RiskyPattern(
                    package=dep.name,
                    pattern_type="unpinned",
                    severity="medium",
                    description=f"'{dep.name}' has an unpinned version ({dep.version}).",
                    recommendation="Pin to a specific version to prevent supply chain attacks.",
                ))

        # Check for excessive dev dependencies in production
        dev_count = len([d for d in deps if d.is_dev])
        total = len(deps)
        if total > 0 and dev_count / total > 0.7:
            patterns.append(RiskyPattern(
                package="(project-level)",
                pattern_type="dev-heavy",
                severity="low",
                description=f"{dev_count}/{total} dependencies are dev-only. Large dev surface increases supply chain risk.",
                recommendation="Review dev dependencies. Remove unused ones. Consider using --production for installs.",
            ))

        return patterns
