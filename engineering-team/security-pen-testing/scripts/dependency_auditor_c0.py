# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_auditor_base import *  # noqa: F403,E402
from dependency_auditor_p0 import Dependency  # noqa: F401,E501


class DependencyAuditorMixin0:
    """Analyze package manifests for known vulnerable patterns and risky dependencies."""
    KNOWN_VULNS = [
        {"ecosystem": "npm", "package": "lodash", "below": "4.17.21",
         "cve": "CVE-2021-23337", "severity": "high", "cvss": 7.2,
         "title": "Prototype Pollution in lodash",
         "description": "lodash before 4.17.21 is vulnerable to Command Injection via template function.",
         "remediation": "Upgrade lodash to >=4.17.21"},
        {"ecosystem": "npm", "package": "axios", "below": "1.6.0",
         "cve": "CVE-2023-45857", "severity": "medium", "cvss": 6.5,
         "title": "CSRF token exposure in axios",
         "description": "axios before 1.6.0 inadvertently exposes CSRF tokens in cross-site requests.",
         "remediation": "Upgrade axios to >=1.6.0"},
        {"ecosystem": "npm", "package": "express", "below": "4.19.2",
         "cve": "CVE-2024-29041", "severity": "medium", "cvss": 6.1,
         "title": "Open Redirect in express",
         "description": "express before 4.19.2 allows open redirects via malicious URLs.",
         "remediation": "Upgrade express to >=4.19.2"},
        {"ecosystem": "npm", "package": "jsonwebtoken", "below": "9.0.0",
         "cve": "CVE-2022-23529", "severity": "critical", "cvss": 9.8,
         "title": "Insecure key retrieval in jsonwebtoken",
         "description": "jsonwebtoken before 9.0.0 allows key confusion attacks via secretOrPublicKey.",
         "remediation": "Upgrade jsonwebtoken to >=9.0.0"},
        {"ecosystem": "npm", "package": "minimatch", "below": "3.0.5",
         "cve": "CVE-2022-3517", "severity": "high", "cvss": 7.5,
         "title": "ReDoS in minimatch",
         "description": "minimatch before 3.0.5 is vulnerable to Regular Expression Denial of Service.",
         "remediation": "Upgrade minimatch to >=3.0.5"},
        {"ecosystem": "npm", "package": "tar", "below": "6.1.9",
         "cve": "CVE-2021-37713", "severity": "high", "cvss": 8.6,
         "title": "Arbitrary File Creation in tar",
         "description": "tar before 6.1.9 allows arbitrary file creation/overwrite via symlinks.",
         "remediation": "Upgrade tar to >=6.1.9"},
        {"ecosystem": "pypi", "package": "pillow", "below": "9.3.0",
         "cve": "CVE-2022-45198", "severity": "high", "cvss": 7.5,
         "title": "DoS via crafted image in Pillow",
         "description": "Pillow before 9.3.0 allows denial of service via specially crafted image files.",
         "remediation": "Upgrade Pillow to >=9.3.0"},
        {"ecosystem": "pypi", "package": "django", "below": "4.2.8",
         "cve": "CVE-2023-46695", "severity": "high", "cvss": 7.5,
         "title": "DoS via file uploads in Django",
         "description": "Django before 4.2.8 allows denial of service via large file uploads.",
         "remediation": "Upgrade Django to >=4.2.8"},
        {"ecosystem": "pypi", "package": "flask", "below": "2.3.2",
         "cve": "CVE-2023-30861", "severity": "high", "cvss": 7.5,
         "title": "Session cookie exposure in Flask",
         "description": "Flask before 2.3.2 may expose session cookies on cross-origin redirects.",
         "remediation": "Upgrade Flask to >=2.3.2"},
        {"ecosystem": "pypi", "package": "requests", "below": "2.31.0",
         "cve": "CVE-2023-32681", "severity": "medium", "cvss": 6.1,
         "title": "Proxy-Authorization header leak in requests",
         "description": "requests before 2.31.0 leaks Proxy-Authorization headers on redirects.",
         "remediation": "Upgrade requests to >=2.31.0"},
        {"ecosystem": "pypi", "package": "cryptography", "below": "41.0.0",
         "cve": "CVE-2023-38325", "severity": "high", "cvss": 7.5,
         "title": "NULL dereference in cryptography",
         "description": "cryptography before 41.0.0 has a NULL pointer dereference in PKCS7 parsing.",
         "remediation": "Upgrade cryptography to >=41.0.0"},
        {"ecosystem": "pypi", "package": "pyyaml", "below": "6.0.1",
         "cve": "CVE-2020-14343", "severity": "critical", "cvss": 9.8,
         "title": "Arbitrary code execution in PyYAML",
         "description": "PyYAML before 6.0.1 allows arbitrary code execution via yaml.load().",
         "remediation": "Upgrade PyYAML to >=6.0.1 and use yaml.safe_load()"},
        {"ecosystem": "go", "package": "golang.org/x/crypto", "below": "0.17.0",
         "cve": "CVE-2023-48795", "severity": "medium", "cvss": 5.9,
         "title": "Terrapin SSH prefix truncation attack",
         "description": "golang.org/x/crypto before 0.17.0 vulnerable to SSH prefix truncation.",
         "remediation": "Upgrade golang.org/x/crypto to >=0.17.0"},
        {"ecosystem": "go", "package": "golang.org/x/net", "below": "0.17.0",
         "cve": "CVE-2023-44487", "severity": "high", "cvss": 7.5,
         "title": "HTTP/2 rapid reset DoS",
         "description": "golang.org/x/net before 0.17.0 vulnerable to HTTP/2 rapid reset attack.",
         "remediation": "Upgrade golang.org/x/net to >=0.17.0"},
        {"ecosystem": "rubygems", "package": "rails", "below": "7.0.8",
         "cve": "CVE-2023-44487", "severity": "high", "cvss": 7.5,
         "title": "ReDoS in Rails",
         "description": "Rails before 7.0.8 vulnerable to Regular Expression Denial of Service.",
         "remediation": "Upgrade rails to >=7.0.8"},
    ]
    TYPOSQUAT_PACKAGES = {
        "npm": ["crossenv", "event-stream-malicious", "flatmap-stream", "ua-parser-jss",
                 "loadsh", "lodashs", "axois", "requets"],
        "pypi": ["python3-dateutil", "jeIlyfish", "python-binance-sdk", "requestss",
                 "djago", "flassk", "requets"],
    }
    def __init__(self, manifest_path: str, severity_filter: str = "low"):
        self.manifest_path = Path(manifest_path)
        self.severity_filter = severity_filter
        self.severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        self.min_severity = self.severity_order.get(severity_filter, 1)
    def audit(self) -> Dict:
        """Run full audit on the manifest file."""
        deps = self._parse_manifest()
        vuln_findings = self._check_vulnerabilities(deps)
        risky_patterns = self._check_risky_patterns(deps)

        # Filter by severity
        vuln_findings = [f for f in vuln_findings
                         if self.severity_order.get(f.severity, 0) >= self.min_severity]
        risky_patterns = [r for r in risky_patterns
                          if self.severity_order.get(r.severity, 0) >= self.min_severity]

        return {
            "manifest": str(self.manifest_path),
            "ecosystem": deps[0].ecosystem if deps else "unknown",
            "total_dependencies": len(deps),
            "dev_dependencies": len([d for d in deps if d.is_dev]),
            "vulnerability_findings": vuln_findings,
            "risky_patterns": risky_patterns,
            "summary": {
                "critical": len([f for f in vuln_findings if f.severity == "critical"]),
                "high": len([f for f in vuln_findings if f.severity == "high"]),
                "medium": len([f for f in vuln_findings if f.severity == "medium"]),
                "low": len([f for f in vuln_findings if f.severity == "low"]),
                "risky_patterns_count": len(risky_patterns),
            }
        }
    def _parse_manifest(self) -> List[Dependency]:
        """Detect manifest type and parse dependencies."""
        name = self.manifest_path.name.lower()
        try:
            content = self.manifest_path.read_text(encoding="utf-8")
        except (OSError, PermissionError) as e:
            print(f"Error reading {self.manifest_path}: {e}", file=sys.stderr)
            sys.exit(1)

        if name == "package.json":
            return self._parse_package_json(content)
        elif name in ("requirements.txt", "requirements-dev.txt", "requirements_dev.txt"):
            return self._parse_requirements(content)
        elif name == "go.mod":
            return self._parse_go_mod(content)
        elif name in ("gemfile", "gemfile.lock"):
            return self._parse_gemfile(content)
        else:
            print(f"Unsupported manifest type: {name}", file=sys.stderr)
            print("Supported: package.json, requirements.txt, go.mod, Gemfile", file=sys.stderr)
            sys.exit(1)
    def _parse_package_json(self, content: str) -> List[Dependency]:
        """Parse npm package.json."""
        deps = []
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in package.json: {e}", file=sys.stderr)
            sys.exit(1)

        for name, version in data.get("dependencies", {}).items():
            clean_ver = re.sub(r"[^0-9.]", "", version).strip(".")
            deps.append(Dependency(name=name, version=clean_ver or version, ecosystem="npm", is_dev=False))
        for name, version in data.get("devDependencies", {}).items():
            clean_ver = re.sub(r"[^0-9.]", "", version).strip(".")
            deps.append(Dependency(name=name, version=clean_ver or version, ecosystem="npm", is_dev=True))
        return deps
    def _parse_requirements(self, content: str) -> List[Dependency]:
        """Parse pip requirements.txt."""
        deps = []
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            match = re.match(r"^([a-zA-Z0-9_.-]+)\s*(?:[=<>!~]+\s*)?([\d.]*)", line)
            if match:
                name, version = match.group(1), match.group(2) or "unknown"
                deps.append(Dependency(name=name.lower(), version=version, ecosystem="pypi"))
        return deps
    def _parse_go_mod(self, content: str) -> List[Dependency]:
        """Parse Go go.mod."""
        deps = []
        in_require = False
        for line in content.strip().split("\n"):
            line = line.strip()
            if line.startswith("require ("):
                in_require = True
                continue
            if line == ")":
                in_require = False
                continue
            if in_require or line.startswith("require "):
                cleaned = line.replace("require ", "").strip()
                parts = cleaned.split()
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1].lstrip("v")
                    indirect = "// indirect" in line
                    deps.append(Dependency(name=name, version=version, ecosystem="go", is_dev=indirect))
        return deps
