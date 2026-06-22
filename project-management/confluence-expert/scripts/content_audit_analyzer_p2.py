# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_audit_analyzer_base import *  # noqa: F403,E402
# fmt: off
from content_audit_analyzer_p1 import OVERSIZED_WORD_THRESHOLD  # noqa: E402,E501
# fmt: on


def check_size_balance(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check for oversized or undersized pages."""
    oversized = []
    undersized = []
    word_counts = []

    for page in pages:
        word_count = page.get("word_count", 0)
        word_counts.append(word_count)

        if word_count > OVERSIZED_WORD_THRESHOLD:
            oversized.append({
                "title": page.get("title", "Untitled"),
                "word_count": word_count,
                "recommendation": "Split into multiple focused pages",
            })
        elif word_count < 50 and word_count > 0:
            undersized.append({
                "title": page.get("title", "Untitled"),
                "word_count": word_count,
                "recommendation": "Expand content or merge with related page",
            })

    total = len(pages)
    well_sized = total - len(oversized) - len(undersized)
    balance_ratio = well_sized / total if total > 0 else 1
    score = max(0, balance_ratio * 100)
    avg_words = sum(word_counts) / total if total > 0 else 0

    return {
        "score": score,
        "oversized_pages": oversized,
        "undersized_pages": undersized,
        "oversized_count": len(oversized),
        "undersized_count": len(undersized),
        "average_word_count": round(avg_words),
    }
def check_completeness(pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check pages for required metadata completeness."""
    incomplete = []
    required_fields = ["title", "last_modified", "author"]

    for page in pages:
        missing = [f for f in required_fields if not page.get(f)]
        if missing:
            incomplete.append({
                "title": page.get("title", "Untitled"),
                "missing_fields": missing,
            })

    total = len(pages)
    complete_ratio = 1 - (len(incomplete) / total) if total > 0 else 1
    score = max(0, complete_ratio * 100)

    return {
        "score": score,
        "incomplete_pages": incomplete,
        "incomplete_count": len(incomplete),
        "complete_count": total - len(incomplete),
    }
def _generate_action_items(dimensions: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate prioritized action items from audit findings."""
    items = []

    # Freshness actions
    freshness = dimensions.get("freshness", {})
    if freshness.get("outdated_count", 0) > 0:
        items.append({
            "priority": "high",
            "action": f"Review and update or archive {freshness['outdated_count']} outdated pages (>180 days old)",
            "category": "freshness",
        })
    if freshness.get("stale_count", 0) > 0:
        items.append({
            "priority": "medium",
            "action": f"Review {freshness['stale_count']} stale pages (90-180 days old) for relevance",
            "category": "freshness",
        })

    # Engagement actions
    engagement = dimensions.get("engagement", {})
    if engagement.get("low_engagement_count", 0) > 0:
        items.append({
            "priority": "medium",
            "action": f"Investigate {engagement['low_engagement_count']} low-engagement pages - consider improving discoverability or archiving",
            "category": "engagement",
        })

    # Organization actions
    organization = dimensions.get("organization", {})
    if organization.get("orphaned_count", 0) > 0:
        items.append({
            "priority": "medium",
            "action": f"Add labels to {organization['orphaned_count']} orphaned pages for better categorization",
            "category": "organization",
        })

    # Size actions
    size = dimensions.get("size_balance", {})
    if size.get("oversized_count", 0) > 0:
        items.append({
            "priority": "low",
            "action": f"Split {size['oversized_count']} oversized pages (>5000 words) into focused sub-pages",
            "category": "size",
        })

    # Completeness actions
    completeness = dimensions.get("completeness", {})
    if completeness.get("incomplete_count", 0) > 0:
        items.append({
            "priority": "low",
            "action": f"Fill in missing metadata for {completeness['incomplete_count']} incomplete pages",
            "category": "completeness",
        })

    return items
