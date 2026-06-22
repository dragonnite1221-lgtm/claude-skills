# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402
from dep_scanner_p0 import Vulnerability  # noqa: F401,E501


class DependencyScannerMixin1:
    def _load_vulnerability_database(self) -> Dict[str, List[Vulnerability]]:
        """Load built-in vulnerability database with common CVE patterns."""
        return {
            # JavaScript/Node.js vulnerabilities
            'lodash': [
                Vulnerability(
                    id='CVE-2021-23337',
                    summary='Prototype pollution in lodash',
                    severity='HIGH',
                    cvss_score=7.2,
                    affected_versions='<4.17.21',
                    fixed_version='4.17.21',
                    published_date='2021-02-15',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2021-23337']
                )
            ],
            'axios': [
                Vulnerability(
                    id='CVE-2023-45857',
                    summary='Cross-site request forgery in axios',
                    severity='MEDIUM',
                    cvss_score=6.1,
                    affected_versions='>=1.0.0 <1.6.0',
                    fixed_version='1.6.0',
                    published_date='2023-10-11',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2023-45857']
                )
            ],
            'express': [
                Vulnerability(
                    id='CVE-2022-24999',
                    summary='Open redirect in express',
                    severity='MEDIUM',
                    cvss_score=6.1,
                    affected_versions='<4.18.2',
                    fixed_version='4.18.2',
                    published_date='2022-11-26',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2022-24999']
                )
            ],
            
            # Python vulnerabilities
            'django': [
                Vulnerability(
                    id='CVE-2024-27351',
                    summary='SQL injection in Django',
                    severity='HIGH',
                    cvss_score=9.8,
                    affected_versions='>=3.2 <4.2.11',
                    fixed_version='4.2.11',
                    published_date='2024-02-06',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2024-27351']
                )
            ],
            'requests': [
                Vulnerability(
                    id='CVE-2023-32681',
                    summary='Proxy-authorization header leak in requests',
                    severity='MEDIUM',
                    cvss_score=6.1,
                    affected_versions='>=2.3.0 <2.31.0',
                    fixed_version='2.31.0',
                    published_date='2023-05-26',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2023-32681']
                )
            ],
            'pillow': [
                Vulnerability(
                    id='CVE-2023-50447',
                    summary='Arbitrary code execution in Pillow',
                    severity='HIGH',
                    cvss_score=8.8,
                    affected_versions='<10.2.0',
                    fixed_version='10.2.0',
                    published_date='2024-01-02',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2023-50447']
                )
            ],
            
            # Go vulnerabilities
            'github.com/gin-gonic/gin': [
                Vulnerability(
                    id='CVE-2023-26125',
                    summary='Path traversal in gin',
                    severity='HIGH',
                    cvss_score=7.5,
                    affected_versions='<1.9.1',
                    fixed_version='1.9.1',
                    published_date='2023-02-28',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2023-26125']
                )
            ],
            
            # Rust vulnerabilities
            'serde': [
                Vulnerability(
                    id='RUSTSEC-2022-0061',
                    summary='Deserialization vulnerability in serde',
                    severity='HIGH',
                    cvss_score=8.2,
                    affected_versions='<1.0.152',
                    fixed_version='1.0.152',
                    published_date='2022-12-07',
                    references=['https://rustsec.org/advisories/RUSTSEC-2022-0061']
                )
            ],
            
            # Ruby vulnerabilities
            'rails': [
                Vulnerability(
                    id='CVE-2023-28362',
                    summary='ReDoS vulnerability in Rails',
                    severity='HIGH',
                    cvss_score=7.5,
                    affected_versions='>=7.0.0 <7.0.4.3',
                    fixed_version='7.0.4.3',
                    published_date='2023-03-13',
                    references=['https://nvd.nist.gov/vuln/detail/CVE-2023-28362']
                )
            ]
        }
