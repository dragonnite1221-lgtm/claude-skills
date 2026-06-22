# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_signal_analyzer_base import *  # noqa: F403,E402
# fmt: off
from threat_signal_analyzer_p1 import IOC_MAX_AGE_DAYS, IOC_SWEEP_TARGETS  # noqa: E402,E501
# fmt: on


def ioc_mode(args):
    """Process IOC list and emit sweep targets with freshness check."""
    ioc_file = getattr(args, "ioc_file", None)
    ioc_date_str = getattr(args, "ioc_date", None)

    if not ioc_file:
        return {
            "mode": "ioc",
            "error": "--ioc-file is required for ioc mode",
        }

    try:
        with open(ioc_file, "r", encoding="utf-8") as fh:
            ioc_data = json.load(fh)
    except FileNotFoundError:
        return {"mode": "ioc", "error": f"IOC file not found: {ioc_file}"}
    except json.JSONDecodeError as exc:
        return {"mode": "ioc", "error": f"Invalid JSON in IOC file: {exc}"}

    # Normalise: accept both plural and singular key names
    type_key_map = {
        "ip": ["ip", "ips"],
        "domain": ["domain", "domains"],
        "hash": ["hash", "hashes"],
        "url": ["url", "urls"],
        "email": ["email", "emails"],
        "user_agent": ["user_agent", "user_agents"],
    }

    ioc_counts = {}
    ioc_values = {}  # type -> list of values
    for ioc_type, candidate_keys in type_key_map.items():
        for ck in candidate_keys:
            if ck in ioc_data:
                vals = ioc_data[ck]
                if isinstance(vals, list) and vals:
                    ioc_counts[ioc_type] = len(vals)
                    ioc_values[ioc_type] = vals
                break

    # Freshness check
    freshness_warning = False
    ioc_age_days = None
    if ioc_date_str:
        try:
            ioc_date = datetime.strptime(ioc_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            now = datetime.now(tz=timezone.utc)
            ioc_age_days = (now - ioc_date).days
            if ioc_age_days > IOC_MAX_AGE_DAYS:
                freshness_warning = True
        except ValueError:
            pass  # invalid date format — skip freshness check

    # Build sweep plan
    sweep_plan = {}
    for ioc_type, count in ioc_counts.items():
        stale = freshness_warning  # applies to entire IOC batch
        sweep_plan[ioc_type] = {
            "count": count,
            "targets": IOC_SWEEP_TARGETS.get(ioc_type, []),
            "stale": stale,
        }

    # Coverage score: ratio of represented IOC types to total possible
    coverage_score = round(len(ioc_counts) / len(IOC_SWEEP_TARGETS), 4) if IOC_SWEEP_TARGETS else 0.0

    # Recommended action
    if freshness_warning:
        recommended_action = (
            "IOCs are stale (>{} days old). Re-validate against current threat intel feeds "
            "before sweeping. Prioritise re-enrichment in threat intel platform.".format(IOC_MAX_AGE_DAYS)
        )
    elif not ioc_counts:
        recommended_action = "No valid IOC types found in file. Verify JSON structure: expected keys ip, domain, hash, url, email."
    elif coverage_score < 0.5:
        recommended_action = (
            "Partial IOC coverage ({:.0%}). Supplement with additional IOC types for broader detection fidelity. "
            "Begin sweep in parallel.".format(coverage_score)
        )
    else:
        recommended_action = (
            "IOC set covers {:.0%} of sweep targets. Initiate concurrent sweep across all listed log sources. "
            "Escalate any matches immediately.".format(coverage_score)
        )

    result = {
        "mode": "ioc",
        "ioc_counts": ioc_counts,
        "sweep_plan": sweep_plan,
        "coverage_score": coverage_score,
        "freshness_warning": freshness_warning,
        "ioc_age_days": ioc_age_days,
        "recommended_action": recommended_action,
    }
    return result
