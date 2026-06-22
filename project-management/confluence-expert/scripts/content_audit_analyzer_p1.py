# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_audit_analyzer_base import *  # noqa: F403,E402


STALE_THRESHOLD_DAYS = 90
OUTDATED_THRESHOLD_DAYS = 180
LOW_VIEW_THRESHOLD = 5
OVERSIZED_WORD_THRESHOLD = 5000
IDEAL_WORD_RANGE = (200, 3000)
HEALTH_WEIGHTS = {
    "freshness": 0.30,
    "engagement": 0.25,
    "organization": 0.20,
    "size_balance": 0.15,
    "completeness": 0.10,
}
def _parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in common formats."""
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None
def check_stale_pages(
    pages: List[Dict[str, Any]],
    reference_date: datetime,
) -> Dict[str, Any]:
    """Identify pages not updated within the stale threshold."""
    stale = []
    outdated = []

    for page in pages:
        last_modified = _parse_date(page.get("last_modified", ""))
        if not last_modified:
            continue

        days_since_update = (reference_date - last_modified).days

        if days_since_update > OUTDATED_THRESHOLD_DAYS:
            outdated.append({
                "title": page.get("title", "Untitled"),
                "days_since_update": days_since_update,
                "last_modified": page.get("last_modified", ""),
                "author": page.get("author", "unknown"),
            })
        elif days_since_update > STALE_THRESHOLD_DAYS:
            stale.append({
                "title": page.get("title", "Untitled"),
                "days_since_update": days_since_update,
                "last_modified": page.get("last_modified", ""),
                "author": page.get("author", "unknown"),
            })

    total = len(pages)
    stale_count = len(stale) + len(outdated)
    fresh_ratio = 1 - (stale_count / total) if total > 0 else 1
    score = max(0, fresh_ratio * 100)

    return {
        "score": score,
        "stale_pages": stale,
        "outdated_pages": outdated,
        "stale_count": len(stale),
        "outdated_count": len(outdated),
        "fresh_count": total - stale_count,
    }
def check_engagement(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identify low-engagement pages based on view counts."""
    low_engagement = []
    view_counts = []

    for page in pages:
        views = page.get("view_count", 0)
        view_counts.append(views)

        if views < LOW_VIEW_THRESHOLD:
            low_engagement.append({
                "title": page.get("title", "Untitled"),
                "view_count": views,
                "author": page.get("author", "unknown"),
            })

    total = len(pages)
    avg_views = sum(view_counts) / total if total > 0 else 0
    engaged_ratio = 1 - (len(low_engagement) / total) if total > 0 else 1
    score = max(0, engaged_ratio * 100)

    return {
        "score": score,
        "low_engagement_pages": low_engagement,
        "low_engagement_count": len(low_engagement),
        "average_views": round(avg_views, 1),
        "max_views": max(view_counts) if view_counts else 0,
        "min_views": min(view_counts) if view_counts else 0,
    }
def check_organization(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identify orphaned pages with no labels."""
    orphaned = []

    for page in pages:
        labels = page.get("labels", [])
        if not labels:
            orphaned.append({
                "title": page.get("title", "Untitled"),
                "author": page.get("author", "unknown"),
            })

    total = len(pages)
    labeled_ratio = 1 - (len(orphaned) / total) if total > 0 else 1
    score = max(0, labeled_ratio * 100)

    # Collect label distribution
    label_counts = {}
    for page in pages:
        for label in page.get("labels", []):
            label_counts[label] = label_counts.get(label, 0) + 1

    return {
        "score": score,
        "orphaned_pages": orphaned,
        "orphaned_count": len(orphaned),
        "labeled_count": total - len(orphaned),
        "label_distribution": dict(sorted(label_counts.items(), key=lambda x: -x[1])[:20]),
    }
