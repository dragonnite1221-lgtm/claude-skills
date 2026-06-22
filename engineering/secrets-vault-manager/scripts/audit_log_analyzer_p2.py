# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from audit_log_analyzer_base import *  # noqa: F403,E402
# fmt: off
from audit_log_analyzer_p1 import extract_fields  # noqa: E402,E501
# fmt: on


def analyze(entries, threshold):
    """Run anomaly detection across all log entries."""
    parsed = [extract_fields(e) for e in entries]

    # Counters
    access_by_identity = defaultdict(int)
    access_by_path = defaultdict(int)
    access_by_ip = defaultdict(set)        # identity -> set of IPs
    ip_to_identities = defaultdict(set)    # IP -> set of identities
    failed_by_source = defaultdict(int)
    off_hours_access = []
    path_by_identity = defaultdict(set)    # identity -> set of paths
    hourly_distribution = defaultdict(int)

    for p in parsed:
        identity = p["identity"]
        path = p["path"]
        ip = p["remote_address"]
        status = p["status_code"]
        hour = p["hour"]

        access_by_identity[identity] += 1
        access_by_path[path] += 1
        access_by_ip[identity].add(ip)
        ip_to_identities[ip].add(identity)
        path_by_identity[identity].add(path)

        if hour is not None:
            hourly_distribution[hour] += 1

        # Failed access (non-200 or 4xx/5xx)
        if status and (status >= 400 or status == 0):
            failed_by_source[f"{identity}@{ip}"] += 1

        # Off-hours: before 6 AM or after 10 PM
        if hour is not None and (hour < 6 or hour >= 22):
            off_hours_access.append(p)

    # Build anomalies
    anomalies = []

    # 1. Volume spikes — identities accessing secrets more than threshold * average
    if access_by_identity:
        avg_access = sum(access_by_identity.values()) / len(access_by_identity)
        spike_threshold = max(threshold * avg_access, threshold)
        for identity, count in access_by_identity.items():
            if count >= spike_threshold:
                anomalies.append({
                    "type": "volume_spike",
                    "severity": "HIGH",
                    "identity": identity,
                    "access_count": count,
                    "threshold": round(spike_threshold, 1),
                    "description": f"Identity '{identity}' made {count} accesses (threshold: {round(spike_threshold, 1)})",
                })

    # 2. Multi-IP access — single identity from many IPs
    for identity, ips in access_by_ip.items():
        if len(ips) >= threshold:
            anomalies.append({
                "type": "multi_ip_access",
                "severity": "MEDIUM",
                "identity": identity,
                "ip_count": len(ips),
                "ips": sorted(ips),
                "description": f"Identity '{identity}' accessed from {len(ips)} different IPs",
            })

    # 3. Failed access attempts
    for source, count in failed_by_source.items():
        if count >= threshold:
            anomalies.append({
                "type": "failed_access",
                "severity": "HIGH",
                "source": source,
                "failure_count": count,
                "description": f"Source '{source}' had {count} failed access attempts",
            })

    # 4. Off-hours access
    if off_hours_access:
        off_hours_identities = defaultdict(int)
        for p in off_hours_access:
            off_hours_identities[p["identity"]] += 1

        for identity, count in off_hours_identities.items():
            if count >= max(threshold, 2):
                anomalies.append({
                    "type": "off_hours_access",
                    "severity": "MEDIUM",
                    "identity": identity,
                    "access_count": count,
                    "description": f"Identity '{identity}' made {count} accesses outside business hours (before 6 AM / after 10 PM)",
                })

    # 5. Broad path access — single identity touching many paths
    for identity, paths in path_by_identity.items():
        if len(paths) >= threshold * 2:
            anomalies.append({
                "type": "broad_access",
                "severity": "MEDIUM",
                "identity": identity,
                "path_count": len(paths),
                "paths": sorted(paths)[:10],
                "description": f"Identity '{identity}' accessed {len(paths)} distinct secret paths",
            })

    # Sort anomalies by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    anomalies.sort(key=lambda x: severity_order.get(x["severity"], 4))

    # Summary stats
    summary = {
        "total_entries": len(entries),
        "parsed_entries": len(parsed),
        "unique_identities": len(access_by_identity),
        "unique_paths": len(access_by_path),
        "unique_source_ips": len(ip_to_identities),
        "total_failures": sum(failed_by_source.values()),
        "off_hours_events": len(off_hours_access),
        "anomalies_found": len(anomalies),
    }

    # Top accessed paths
    top_paths = sorted(access_by_path.items(), key=lambda x: -x[1])[:10]

    return {
        "summary": summary,
        "anomalies": anomalies,
        "top_accessed_paths": [{"path": p, "count": c} for p, c in top_paths],
        "hourly_distribution": dict(sorted(hourly_distribution.items())),
    }
