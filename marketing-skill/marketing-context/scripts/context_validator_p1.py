# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from context_validator_base import *  # noqa: F403,E402


SECTIONS = {
    "Product Overview": {"required": True, "weight": 10, "markers": ["one-liner", "what it does", "product category", "business model"]},
    "Target Audience": {"required": True, "weight": 12, "markers": ["target compan", "decision-maker", "use case", "jobs to be done"]},
    "Personas": {"required": False, "weight": 5, "markers": ["persona", "champion", "decision maker"]},
    "Problems & Pain Points": {"required": True, "weight": 10, "markers": ["core problem", "fall short", "cost", "tension"]},
    "Competitive Landscape": {"required": True, "weight": 10, "markers": ["direct", "competitor", "secondary"]},
    "Differentiation": {"required": True, "weight": 10, "markers": ["differentiator", "differently", "why customers choose"]},
    "Objections": {"required": False, "weight": 5, "markers": ["objection", "response", "anti-persona"]},
    "Switching Dynamics": {"required": False, "weight": 5, "markers": ["push", "pull", "habit", "anxiety"]},
    "Customer Language": {"required": True, "weight": 10, "markers": ["verbatim", "words to use", "words to avoid"]},
    "Brand Voice": {"required": True, "weight": 8, "markers": ["tone", "style", "personality"]},
    "Style Guide": {"required": False, "weight": 3, "markers": ["grammar", "capitalization", "formatting"]},
    "Proof Points": {"required": True, "weight": 7, "markers": ["metric", "customer", "testimonial"]},
    "Content & SEO": {"required": False, "weight": 3, "markers": ["keyword", "internal link"]},
    "Goals": {"required": True, "weight": 2, "markers": ["business goal", "conversion"]}
}
def validate_context(content: str) -> dict:
    """Validate marketing context file and return score."""
    content_lower = content.lower()
    results = {"sections": {}, "score": 0, "max_score": 100, "missing_required": [], "missing_optional": [], "warnings": []}
    total_weight = sum(s["weight"] for s in SECTIONS.values())
    earned = 0

    for name, config in SECTIONS.items():
        section_present = name.lower().replace("& ", "").replace("  ", " ") in content_lower or any(
            m in content_lower for m in config["markers"][:2]
        )

        markers_found = sum(1 for m in config["markers"] if m in content_lower)
        markers_total = len(config["markers"])

        has_placeholder = bool(re.search(r'\[.*?\]', content[content_lower.find(name.lower()):content_lower.find(name.lower()) + 500] if name.lower() in content_lower else ""))

        if section_present and markers_found > 0:
            completeness = markers_found / markers_total
            if has_placeholder and completeness < 0.5:
                completeness *= 0.5  # Penalize unfilled templates
            section_score = round(config["weight"] * completeness)
            earned += section_score
            status = "complete" if completeness >= 0.75 else "partial"
        else:
            section_score = 0
            status = "missing"
            if config["required"]:
                results["missing_required"].append(name)
            else:
                results["missing_optional"].append(name)

        results["sections"][name] = {
            "status": status,
            "markers_found": markers_found,
            "markers_total": markers_total,
            "score": section_score,
            "max_score": config["weight"],
            "required": config["required"]
        }

    results["score"] = round((earned / total_weight) * 100)

    # Warnings
    if "verbatim" not in content_lower and '"' not in content:
        results["warnings"].append("No verbatim customer quotes found — copy will sound generic")
    if not re.search(r'\d+%|\$\d+|\d+ customer', content_lower):
        results["warnings"].append("No metrics or proof points with numbers found")
    if "last updated" in content_lower:
        date_match = re.search(r'last updated:?\s*(\d{4}-\d{2}-\d{2})', content_lower)
        if date_match:
            from datetime import datetime
            try:
                updated = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                age_days = (datetime.now() - updated).days
                if age_days > 180:
                    results["warnings"].append(f"Context is {age_days} days old — review recommended (>180 days)")
            except ValueError:
                pass

    return results
def print_report(results: dict):
    """Print human-readable validation report."""
    print(f"\n{'='*50}")
    print(f"MARKETING CONTEXT VALIDATION")
    print(f"{'='*50}")
    print(f"\nOverall Score: {results['score']}/100")
    print(f"{'🟢 Strong' if results['score'] >= 80 else '🟡 Needs Work' if results['score'] >= 50 else '🔴 Incomplete'}")

    print(f"\n{'─'*50}")
    print(f"{'Section':<25} {'Status':<10} {'Score':<10}")
    print(f"{'─'*50}")
    for name, data in results["sections"].items():
        icon = {"complete": "✅", "partial": "⚠️", "missing": "❌"}[data["status"]]
        req = " *" if data["required"] else ""
        print(f"{icon} {name:<23} {data['status']:<10} {data['score']}/{data['max_score']}{req}")

    if results["missing_required"]:
        print(f"\n🔴 Missing Required Sections:")
        for s in results["missing_required"]:
            print(f"   → {s}")

    if results["missing_optional"]:
        print(f"\n🟡 Missing Optional Sections:")
        for s in results["missing_optional"]:
            print(f"   → {s}")

    if results["warnings"]:
        print(f"\n⚠️  Warnings:")
        for w in results["warnings"]:
            print(f"   → {w}")

    print(f"\n* = required section")
    print(f"{'='*50}")
