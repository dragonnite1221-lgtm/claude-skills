# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from growth_tracker_base import *  # noqa: F403,E402


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".growth-data")
def get_data_file(handle: str) -> str:
    clean = handle.lstrip("@").lower()
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{clean}.jsonl")
def record_snapshot(handle: str, followers: int, following: int = 0,
                    eng_rate: float = 0, posts_week: float = 0, notes: str = ""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "handle": handle,
        "followers": followers,
        "following": following,
        "engagement_rate": eng_rate,
        "posts_per_week": posts_week,
        "notes": notes,
    }

    filepath = get_data_file(handle)
    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry
def load_snapshots(handle: str, period_days: int = 0) -> list:
    filepath = get_data_file(handle)
    if not os.path.exists(filepath):
        return []

    entries = []
    cutoff = None
    if period_days > 0:
        cutoff = datetime.now() - timedelta(days=period_days)

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if cutoff:
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts < cutoff:
                    continue
            entries.append(entry)

    return entries
def generate_report(handle: str, entries: list) -> dict:
    if not entries:
        return {"handle": handle, "error": "No data found"}

    report = {
        "handle": handle,
        "data_points": len(entries),
        "first_record": entries[0]["timestamp"],
        "last_record": entries[-1]["timestamp"],
        "current_followers": entries[-1]["followers"],
    }

    if len(entries) >= 2:
        first = entries[0]
        last = entries[-1]

        follower_change = last["followers"] - first["followers"]
        days_span = (datetime.fromisoformat(last["timestamp"]) -
                     datetime.fromisoformat(first["timestamp"])).days
        days_span = max(days_span, 1)

        report["follower_change"] = follower_change
        report["days_tracked"] = days_span
        report["daily_growth"] = round(follower_change / days_span, 1)
        report["weekly_growth"] = round((follower_change / days_span) * 7, 1)
        report["monthly_projection"] = round((follower_change / days_span) * 30)

        if first["followers"] > 0:
            pct_change = ((last["followers"] - first["followers"]) / first["followers"]) * 100
            report["growth_percent"] = round(pct_change, 1)

        # Engagement trend
        eng_rates = [e["engagement_rate"] for e in entries if e.get("engagement_rate", 0) > 0]
        if len(eng_rates) >= 2:
            mid = len(eng_rates) // 2
            first_half_avg = sum(eng_rates[:mid]) / mid
            second_half_avg = sum(eng_rates[mid:]) / (len(eng_rates) - mid)
            report["engagement_trend"] = "improving" if second_half_avg > first_half_avg else "declining"
            report["avg_engagement_rate"] = round(sum(eng_rates) / len(eng_rates), 2)

    return report
def project_milestone(handle: str, entries: list, target: int) -> dict:
    if len(entries) < 2:
        return {"error": "Need at least 2 data points for projection"}

    current = entries[-1]["followers"]
    if current >= target:
        return {"handle": handle, "target": target, "status": "Already reached!"}

    first = entries[0]
    last = entries[-1]
    days_span = (datetime.fromisoformat(last["timestamp"]) -
                 datetime.fromisoformat(first["timestamp"])).days
    days_span = max(days_span, 1)

    daily_growth = (last["followers"] - first["followers"]) / days_span

    if daily_growth <= 0:
        return {"handle": handle, "target": target, "status": "Not growing — can't project",
                "daily_growth": round(daily_growth, 1)}

    remaining = target - current
    days_needed = remaining / daily_growth
    target_date = datetime.now() + timedelta(days=days_needed)

    return {
        "handle": handle,
        "current": current,
        "target": target,
        "remaining": remaining,
        "daily_growth": round(daily_growth, 1),
        "days_needed": round(days_needed),
        "projected_date": target_date.strftime("%Y-%m-%d"),
    }
