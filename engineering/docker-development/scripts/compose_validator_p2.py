# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compose_validator_base import *  # noqa: F403,E402


def validate_compose(parsed, strict=False):
    """Run validation rules on parsed compose file."""
    findings = []
    services = parsed.get("services", {})

    # --- Version check ---
    version = parsed.get("version", "")
    if version:
        findings.append({
            "severity": "low",
            "category": "deprecation",
            "message": f"'version: {version}' is deprecated in Compose V2 — remove it",
            "service": "(top-level)",
        })

    # --- Per-service checks ---
    all_ports = []

    for name, svc in services.items():
        # Healthcheck
        if "healthcheck" not in svc:
            findings.append({
                "severity": "medium",
                "category": "reliability",
                "message": f"No healthcheck defined — orchestrator can't detect unhealthy state",
                "service": name,
            })

        # Image tag
        image = svc.get("image", "")
        if image:
            if ":latest" in image:
                findings.append({
                    "severity": "high",
                    "category": "reproducibility",
                    "message": f"Using :latest tag on '{image}' — pin to specific version",
                    "service": name,
                })
            elif ":" not in image and "/" not in image:
                findings.append({
                    "severity": "high",
                    "category": "reproducibility",
                    "message": f"No tag on image '{image}' — defaults to :latest",
                    "service": name,
                })

        # Ports
        ports = svc.get("ports", [])
        if isinstance(ports, list):
            for p in ports:
                p_str = str(p)
                # Extract host port
                match = re.match(r"(\d+):\d+", p_str)
                if match:
                    host_port = match.group(1)
                    all_ports.append((host_port, name))

        # Environment secrets
        env = svc.get("environment", [])
        if isinstance(env, list):
            for e in env:
                e_str = str(e)
                if re.search(r"(?:PASSWORD|SECRET|TOKEN|KEY)=\S+", e_str, re.IGNORECASE):
                    if "env_file" not in svc:
                        findings.append({
                            "severity": "critical",
                            "category": "security",
                            "message": f"Inline secret in environment: {e_str[:40]}...",
                            "service": name,
                        })
        elif isinstance(env, dict):
            for k, v in env.items():
                if re.search(r"(?:PASSWORD|SECRET|TOKEN|KEY)", k, re.IGNORECASE) and v:
                    findings.append({
                        "severity": "critical",
                        "category": "security",
                        "message": f"Inline secret: {k}={str(v)[:20]}...",
                        "service": name,
                    })

        # depends_on without condition
        depends = svc.get("depends_on", [])
        if isinstance(depends, list) and depends:
            findings.append({
                "severity": "medium",
                "category": "reliability",
                "message": "depends_on without condition: service_healthy — race condition risk",
                "service": name,
            })

        # Bind mounts (./path style)
        volumes = svc.get("volumes", [])
        if isinstance(volumes, list):
            for v in volumes:
                v_str = str(v)
                if v_str.startswith("./") or v_str.startswith("/"):
                    if "/var/run/docker.sock" in v_str:
                        findings.append({
                            "severity": "critical",
                            "category": "security",
                            "message": "Docker socket mounted — container has host Docker access",
                            "service": name,
                        })

        # Restart policy
        if "restart" not in svc and "build" not in svc:
            findings.append({
                "severity": "low",
                "category": "reliability",
                "message": "No restart policy — container won't auto-restart on failure",
                "service": name,
            })

        # Resource limits
        if "mem_limit" not in svc and "deploy" not in svc:
            findings.append({
                "severity": "low" if not strict else "medium",
                "category": "resources",
                "message": "No memory limit — container can consume all host memory",
                "service": name,
            })

    # Port conflicts
    port_map = {}
    for port, svc_name in all_ports:
        if port in port_map:
            findings.append({
                "severity": "high",
                "category": "networking",
                "message": f"Port {port} conflict between '{port_map[port]}' and '{svc_name}'",
                "service": svc_name,
            })
        port_map[port] = svc_name

    # Network check
    if "networks" not in parsed or not parsed["networks"]:
        if len(services) > 1:
            findings.append({
                "severity": "low",
                "category": "networking",
                "message": "No explicit networks — all services share default bridge network",
                "service": "(top-level)",
            })

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 4))

    return findings
