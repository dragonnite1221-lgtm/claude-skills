# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from threat_signal_analyzer_base import *  # noqa: F403,E402
# fmt: off
from threat_signal_analyzer_p1 import ANOMALY_TIME_HOURS_SUSPICIOUS  # noqa: E402,E501
# fmt: on


def anomaly_mode(args):
    """Z-score behavioral anomaly detection against a provided baseline."""
    events_file = getattr(args, "events_file", None)
    baseline_mean = getattr(args, "baseline_mean", None)
    baseline_std = getattr(args, "baseline_std", None)

    if not events_file:
        return {"mode": "anomaly", "error": "--events-file is required for anomaly mode"}
    if baseline_mean is None or baseline_std is None:
        return {"mode": "anomaly", "error": "--baseline-mean and --baseline-std are required for anomaly mode"}
    if baseline_std <= 0:
        return {"mode": "anomaly", "error": "--baseline-std must be greater than 0"}

    try:
        with open(events_file, "r", encoding="utf-8") as fh:
            events = json.load(fh)
    except FileNotFoundError:
        return {"mode": "anomaly", "error": f"Events file not found: {events_file}"}
    except json.JSONDecodeError as exc:
        return {"mode": "anomaly", "error": f"Invalid JSON in events file: {exc}"}

    if not isinstance(events, list):
        return {"mode": "anomaly", "error": "Events file must contain a JSON array of event objects"}

    anomaly_events = []
    soft_flag_count = 0
    hard_flag_count = 0
    time_anomaly_count = 0
    entity_counts = {}  # entity -> anomaly count

    for idx, event in enumerate(events):
        if not isinstance(event, dict):
            continue

        volume = event.get("volume")
        timestamp_str = event.get("timestamp", "")
        entity = event.get("entity", f"unknown_{idx}")
        action = event.get("action", "")

        # Z-score calculation
        z_score = None
        soft_flag = False
        hard_flag = False
        if volume is not None:
            try:
                volume = float(volume)
                z_score = (volume - baseline_mean) / baseline_std
                if z_score >= 3.0:
                    hard_flag = True
                    hard_flag_count += 1
                    entity_counts[entity] = entity_counts.get(entity, 0) + 1
                elif z_score >= 2.0:
                    soft_flag = True
                    soft_flag_count += 1
                    entity_counts[entity] = entity_counts.get(entity, 0) + 1
            except (TypeError, ValueError):
                pass

        # Time anomaly check
        time_anomaly = False
        event_hour = None
        if timestamp_str:
            for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    event_hour = dt.hour
                    break
                except ValueError:
                    continue
            # Try with timezone offset via fromisoformat (Python 3.7+)
            if event_hour is None:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    event_hour = dt.hour
                except ValueError:
                    pass

        if event_hour is not None and event_hour in ANOMALY_TIME_HOURS_SUSPICIOUS:
            time_anomaly = True
            time_anomaly_count += 1

        if soft_flag or hard_flag or time_anomaly:
            anomaly_events.append({
                "event_index": idx,
                "entity": entity,
                "action": action,
                "timestamp": timestamp_str,
                "volume": volume,
                "z_score": round(z_score, 4) if z_score is not None else None,
                "soft_flag": soft_flag,
                "hard_flag": hard_flag,
                "time_anomaly": time_anomaly,
                "event_hour": event_hour,
            })

    total_events = len(events)
    risk_score = round(hard_flag_count / total_events, 4) if total_events > 0 else 0.0

    # Top anomalous entities
    top_entities = sorted(entity_counts.items(), key=lambda x: -x[1])[:5]

    # Recommended action
    if hard_flag_count > 0:
        recommended_action = (
            "{} hard anomalies detected (z >= 3.0). Initiate threat hunt and review affected entities: {}. "
            "Escalate to incident response if entity is high-value.".format(
                hard_flag_count,
                ", ".join(e for e, _ in top_entities[:3]) if top_entities else "unknown"
            )
        )
    elif soft_flag_count > 0:
        recommended_action = (
            "{} soft anomalies detected (z >= 2.0). Investigate {} for unusual activity patterns. "
            "Cross-correlate with other log sources.".format(
                soft_flag_count,
                ", ".join(e for e, _ in top_entities[:3]) if top_entities else "unknown"
            )
        )
    elif time_anomaly_count > 0:
        recommended_action = (
            "No volume anomalies, but {} events occurred during suspicious hours (22:00-06:00). "
            "Verify whether this activity is expected for the affected entities.".format(time_anomaly_count)
        )
    else:
        recommended_action = "No anomalies detected. Baseline appears stable for the provided event set."

    result = {
        "mode": "anomaly",
        "total_events": total_events,
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "anomaly_events": anomaly_events,
        "risk_score": risk_score,
        "soft_flag_count": soft_flag_count,
        "hard_flag_count": hard_flag_count,
        "time_anomaly_count": time_anomaly_count,
        "top_anomalous_entities": [{"entity": e, "anomaly_count": c} for e, c in top_entities],
        "recommended_action": recommended_action,
    }
    return result
