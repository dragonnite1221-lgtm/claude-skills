# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tf_security_scanner_base import *  # noqa: F403,E402
# fmt: off
from tf_security_scanner_p2 import NETWORK_PATTERNS  # noqa: E402,E501
# fmt: on


def check_security_groups(content):
    """Custom check for open security groups."""
    findings = []

    # Parse ingress blocks within security group resources
    sg_blocks = re.finditer(
        r'resource\s+"aws_security_group"[^{]*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )

    for sg_match in sg_blocks:
        sg_body = sg_match.group(1)
        ingress_blocks = re.finditer(
            r'ingress\s*\{(.*?)\}', sg_body, re.DOTALL
        )

        for ingress in ingress_blocks:
            block = ingress.group(1)
            has_open_cidr = '0.0.0.0/0' in block or '::/0' in block

            if not has_open_cidr:
                continue

            from_port_match = re.search(r'from_port\s*=\s*(\d+)', block)
            to_port_match = re.search(r'to_port\s*=\s*(\d+)', block)

            if from_port_match and to_port_match:
                from_port = int(from_port_match.group(1))
                to_port = int(to_port_match.group(1))

                # SSH open
                if from_port <= 22 <= to_port:
                    rule = next(r for r in NETWORK_PATTERNS if r["id"] == "SEC020")
                    findings.append({
                        "id": rule["id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "fix": rule["fix"],
                        "line": f"ingress port 22, cidr 0.0.0.0/0",
                    })

                # RDP open
                if from_port <= 3389 <= to_port:
                    rule = next(r for r in NETWORK_PATTERNS if r["id"] == "SEC021")
                    findings.append({
                        "id": rule["id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "fix": rule["fix"],
                        "line": f"ingress port 3389, cidr 0.0.0.0/0",
                    })

                # All ports open
                if from_port == 0 and to_port >= 65535:
                    rule = next(r for r in NETWORK_PATTERNS if r["id"] == "SEC022")
                    findings.append({
                        "id": rule["id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "fix": rule["fix"],
                        "line": f"ingress ports 0-65535, cidr 0.0.0.0/0",
                    })

    return findings
