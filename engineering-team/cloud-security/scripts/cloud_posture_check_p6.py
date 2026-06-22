# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cloud_posture_check_base import *  # noqa: F403,E402
# fmt: off
from cloud_posture_check_p2 import IAMAnalysisResult, IAMFinding, _bump_severity  # noqa: E402,E501
# fmt: on


def check_security_group(
    sg_json: dict,
    source: str,
    severity_modifier: str,
) -> IAMAnalysisResult:
    """
    Check AWS Security Group JSON for dangerous inbound rules.

    Args:
        sg_json:            Parsed Security Group JSON (AWS DescribeSecurityGroups
                            output format or Terraform aws_security_group block).
        source:             Display name / file path.
        severity_modifier:  internet-facing | regulated-data | none.

    Returns:
        IAMAnalysisResult populated with SG findings.
    """
    RISKY_PORTS: Dict[int, str] = {
        22: "SSH",
        3389: "RDP",
        23: "Telnet",
        21: "FTP",
        3306: "MySQL",
        5432: "PostgreSQL",
        1433: "MSSQL",
        27017: "MongoDB",
        6379: "Redis",
    }

    result = IAMAnalysisResult(
        source=source,
        check_mode="sg",
        provider="aws",
        severity_modifier=severity_modifier,
    )
    findings: List[IAMFinding] = []
    fid = 0

    def _next_id() -> str:
        nonlocal fid
        fid += 1
        return f"SG-{fid:03d}"

    # Support both AWS API format (IpPermissions) and Terraform ingress blocks
    ip_permissions = sg_json.get("IpPermissions") or []
    terraform_ingress = sg_json.get("ingress") or []

    # Normalise Terraform ingress blocks to AWS API format
    normalised: List[dict] = list(ip_permissions)
    for ing in terraform_ingress:
        if not isinstance(ing, dict):
            continue
        cidr_blocks = ing.get("cidr_blocks") or []
        ipv6_cidr_blocks = ing.get("ipv6_cidr_blocks") or []
        ip_ranges = [{"CidrIp": c} for c in cidr_blocks]
        ipv6_ranges = [{"CidrIpv6": c} for c in ipv6_cidr_blocks]
        normalised.append({
            "IpProtocol": str(ing.get("protocol", "tcp")),
            "FromPort": ing.get("from_port", 0),
            "ToPort": ing.get("to_port", 65535),
            "IpRanges": ip_ranges,
            "Ipv6Ranges": ipv6_ranges,
        })

    for rule in normalised:
        from_port = rule.get("FromPort", 0)
        to_port = rule.get("ToPort", 65535)
        protocol = str(rule.get("IpProtocol", "tcp"))

        # Collect CIDRs from both IPv4 and IPv6 ranges
        all_ranges: List[Tuple[str, str]] = []
        for ip_range in rule.get("IpRanges", []):
            cidr = ip_range.get("CidrIp", "")
            if cidr:
                all_ranges.append((cidr, "ipv4"))
        for ip_range in rule.get("Ipv6Ranges", []):
            cidr = ip_range.get("CidrIpv6", "")
            if cidr:
                all_ranges.append((cidr, "ipv6"))

        for cidr, ip_ver in all_ranges:
            if cidr not in ("0.0.0.0/0", "::/0"):
                continue  # Not open to the world

            if protocol == "-1":
                # All traffic open to the internet
                severity = _bump_severity("critical", severity_modifier)
                findings.append(IAMFinding(
                    finding_id=_next_id(),
                    category="sg",
                    severity=severity,
                    title="Security Group: All Traffic Open to Internet",
                    description=(
                        f"Inbound rule allows ALL traffic (protocol -1) "
                        f"from {cidr} ({ip_ver}). This exposes every port on every instance "
                        "in this security group to the public internet."
                    ),
                    affected_resource=source,
                    recommendation=(
                        "Remove the all-traffic rule. Define explicit port/protocol "
                        "allowlist rules for only the services that must be internet-accessible."
                    ),
                    mitre_technique="T1190",
                ))
                continue

            # Check port range against RISKY_PORTS
            matched_ports = [
                p for p in RISKY_PORTS
                if from_port <= p <= to_port
            ]

            if matched_ports:
                for port in matched_ports:
                    service = RISKY_PORTS[port]
                    severity = _bump_severity("critical", severity_modifier)
                    findings.append(IAMFinding(
                        finding_id=_next_id(),
                        category="sg",
                        severity=severity,
                        title=f"Security Group: {service} ({port}) Open to Internet",
                        description=(
                            f"Inbound rule allows {service} (port {port}/{protocol}) "
                            f"from {cidr} ({ip_ver}). Direct internet access to {service} "
                            "exposes this service to brute-force, exploitation, and scanning."
                        ),
                        affected_resource=source,
                        recommendation=(
                            f"Restrict port {port} to specific trusted CIDRs or a VPN/bastion. "
                            f"For {service}, consider using AWS Systems Manager Session Manager "
                            "as a zero-trust alternative that requires no open inbound ports."
                        ),
                        mitre_technique="T1133",
                    ))
            else:
                # Open to the internet on a non-standard port
                severity = _bump_severity("high", severity_modifier)
                port_label = (
                    f"port {from_port}"
                    if from_port == to_port
                    else f"ports {from_port}-{to_port}"
                )
                findings.append(IAMFinding(
                    finding_id=_next_id(),
                    category="sg",
                    severity=severity,
                    title=f"Security Group: {port_label.title()} Open to Internet",
                    description=(
                        f"Inbound rule opens {port_label} ({protocol}) to {cidr} ({ip_ver}). "
                        "Broad internet exposure increases attack surface even on non-standard ports."
                    ),
                    affected_resource=source,
                    recommendation=(
                        f"Restrict {port_label} to the specific IP ranges that require access. "
                        "Use Security Group references instead of CIDRs where possible."
                    ),
                    mitre_technique="T1046",
                ))

    result.findings = findings
    result.summary = {
        "total_findings": len(findings),
        "critical": sum(1 for f in findings if f.severity == "critical"),
        "high": sum(1 for f in findings if f.severity == "high"),
        "medium": sum(1 for f in findings if f.severity == "medium"),
        "low": sum(1 for f in findings if f.severity == "low"),
        "check_mode": "sg",
        "provider": "aws",
        "severity_modifier": severity_modifier,
    }
    return result
