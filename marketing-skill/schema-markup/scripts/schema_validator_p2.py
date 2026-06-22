# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_validator_base import *  # noqa: F403,E402
# fmt: off
from schema_validator_p1 import SCHEMA_RULES, detect_type  # noqa: E402,E501
# fmt: on


def score_schema(schema_type: str, obj: Dict) -> Dict:
    """Score a single schema object against known rules. Returns 0-100."""
    if schema_type not in SCHEMA_RULES:
        return {
            "score": 50,
            "status": "unknown_type",
            "required_present": [],
            "required_missing": [],
            "recommended_present": [],
            "recommended_missing": [],
            "notes": [f"No validation rules defined for '{schema_type}' — manual check recommended."],
        }

    rules = SCHEMA_RULES[schema_type]
    required = rules.get("required", [])
    recommended = rules.get("recommended", [])

    required_present = [f for f in required if f in obj and obj[f]]
    required_missing = [f for f in required if f not in obj or not obj[f]]
    recommended_present = [f for f in recommended if f in obj and obj[f]]
    recommended_missing = [f for f in recommended if f not in obj or not obj[f]]

    # Score: required fields = 70 points, recommended = 30 points
    req_score = (len(required_present) / len(required) * 70) if required else 70
    rec_score = (len(recommended_present) / len(recommended) * 30) if recommended else 30
    total_score = int(req_score + rec_score)

    notes = []

    # Type-specific checks
    if schema_type in ("Article", "BlogPosting", "NewsArticle"):
        image = obj.get("image")
        if image:
            img_url = image if isinstance(image, str) else image.get("url", "") if isinstance(image, dict) else ""
            if img_url and not img_url.startswith("http"):
                notes.append("⚠️  'image' URL appears to be relative — must be absolute (https://...)")
        if "datePublished" in obj:
            dp = obj["datePublished"]
            if not re.match(r"\d{4}-\d{2}-\d{2}", str(dp)):
                notes.append("⚠️  'datePublished' should be ISO 8601 format: YYYY-MM-DD")

    if schema_type == "Product":
        offers = obj.get("offers", {})
        if isinstance(offers, dict):
            price = offers.get("price")
            if isinstance(price, str) and any(c in price for c in "$€£¥"):
                notes.append("⚠️  'offers.price' should be numeric (49.99), not a string with currency symbol.")
            avail = offers.get("availability", "")
            if avail and not avail.startswith("https://schema.org/"):
                notes.append("⚠️  'offers.availability' must use full URL: https://schema.org/InStock")

    if schema_type == "FAQPage":
        entities = obj.get("mainEntity", [])
        if isinstance(entities, list):
            for i, q in enumerate(entities):
                if not q.get("acceptedAnswer", {}).get("text"):
                    notes.append(f"⚠️  Question #{i+1} has empty 'acceptedAnswer.text'")

    if schema_type == "BreadcrumbList":
        items = obj.get("itemListElement", [])
        if isinstance(items, list):
            positions = [item.get("position") for item in items if isinstance(item, dict)]
            if sorted(positions) != list(range(1, len(positions) + 1)):
                notes.append("⚠️  'itemListElement' positions must be sequential integers starting at 1.")

    return {
        "score": total_score,
        "status": "valid" if not required_missing else "missing_required",
        "required_present": required_present,
        "required_missing": required_missing,
        "recommended_present": recommended_present,
        "recommended_missing": recommended_missing,
        "notes": notes,
    }
def validate_block(raw_json: str, block_index: int) -> List[Dict]:
    """Parse and validate a single JSON-LD block. Returns list of results (may contain @graph)."""
    results = []
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return [{
            "block": block_index,
            "type": "PARSE_ERROR",
            "score": 0,
            "status": "parse_error",
            "error": str(e),
            "notes": ["❌ JSON is malformed — fix syntax before validation."],
        }]

    # Handle @graph
    objects = data.get("@graph", [data]) if isinstance(data, dict) else [data]

    for obj in objects:
        if not isinstance(obj, dict):
            continue
        schema_type = detect_type(obj)
        if not schema_type:
            results.append({
                "block": block_index,
                "type": "UNKNOWN",
                "score": 0,
                "status": "no_type",
                "notes": ["❌ No '@type' found in schema object."],
            })
            continue

        validation = score_schema(schema_type, obj)
        results.append({
            "block": block_index,
            "type": schema_type,
            **validation,
        })

    return results
def grade(score: int) -> str:
    if score >= 90:
        return "🟢 Excellent"
    if score >= 70:
        return "🟡 Good"
    if score >= 50:
        return "🟠 Needs Work"
    return "🔴 Poor"
