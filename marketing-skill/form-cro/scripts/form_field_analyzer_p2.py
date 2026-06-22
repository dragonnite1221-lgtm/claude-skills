# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from form_field_analyzer_base import *  # noqa: F403,E402


def analyze_form(form):
    """Analyze a single form for CRO issues."""
    fields = form["fields"]
    issues = []
    warnings = []
    positives = []

    field_count = len(fields)

    # Field count analysis
    if field_count > 7:
        issues.append(f"Too many fields ({field_count}). Each field above 3 reduces conversion by ~5-10%. Consider progressive disclosure.")
    elif field_count > 4:
        warnings.append(f"{field_count} fields — acceptable but test reducing to 3-4 core fields.")
    elif field_count <= 3:
        positives.append(f"Low friction — only {field_count} fields.")

    # Phone number field
    phone_fields = [f for f in fields if "phone" in f["name"].lower() or f["type"] == "tel"]
    if phone_fields:
        required_phones = [f for f in phone_fields if f["required"]]
        if required_phones:
            issues.append("Phone number is REQUIRED — this is the #1 form abandonment trigger. Make optional or remove.")
        else:
            warnings.append("Phone field present (optional) — still causes friction. Consider removing unless sales-critical.")

    # Labels
    unlabeled = [f for f in fields if not f["has_label"] and not f["placeholder"]]
    if unlabeled:
        issues.append(f"{len(unlabeled)} fields have no label AND no placeholder. Users won't know what to enter.")

    placeholder_only = [f for f in fields if not f["has_label"] and f["placeholder"]]
    if placeholder_only:
        warnings.append(f"{len(placeholder_only)} fields use placeholder-only labels. Placeholders disappear on focus — use visible labels.")

    # Button text
    weak_ctas = ["submit", "send", "go", "ok"]
    for btn in form["buttons"]:
        if btn.lower() in weak_ctas:
            warnings.append(f'CTA button says "{btn}" — use action-specific text like "Get My Free Report" or "Start Free Trial".')

    if not form["buttons"]:
        issues.append("No submit button found. Form may be broken or use JavaScript submission only.")

    # Autocomplete
    fields_with_autocomplete = [f for f in fields if f["autocomplete"]]
    if not fields_with_autocomplete and field_count > 0:
        warnings.append("No autocomplete attributes. Adding autocomplete reduces mobile friction significantly.")

    # Required fields
    required_count = sum(1 for f in fields if f["required"])
    if required_count == field_count and field_count > 2:
        warnings.append("ALL fields are required. Consider making some optional to reduce perceived commitment.")

    # Score
    score = 100
    score -= len(issues) * 15
    score -= len(warnings) * 5
    score += len(positives) * 5
    score = max(0, min(100, score))

    return {
        "field_count": field_count,
        "required_count": required_count,
        "has_phone": len(phone_fields) > 0,
        "cta_text": form["buttons"],
        "issues": issues,
        "warnings": warnings,
        "positives": positives,
        "score": score,
        "fields": [{"name": f["name"], "type": f["type"], "required": f["required"]} for f in fields]
    }
def format_report(analyses):
    """Format human-readable report."""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  FORM CRO — FIELD ANALYSIS REPORT")
    lines.append("=" * 60)

    for i, analysis in enumerate(analyses):
        lines.append("")
        lines.append(f"  FORM {i + 1}")
        lines.append(f"  Fields: {analysis['field_count']} | Required: {analysis['required_count']} | CTA: {', '.join(analysis['cta_text']) or 'none'}")
        lines.append("")

        score = analysis["score"]
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        lines.append(f"  FORM SCORE: {score}/100")
        lines.append(f"  [{bar}]")
        lines.append("")

        lines.append("  Fields:")
        for f in analysis["fields"]:
            req = " *" if f["required"] else ""
            lines.append(f"    [{f['type']}] {f['name']}{req}")
        lines.append("")

        if analysis["positives"]:
            lines.append("  🟢 STRENGTHS:")
            for p in analysis["positives"]:
                lines.append(f"     ✓ {p}")
            lines.append("")

        if analysis["issues"]:
            lines.append("  🔴 ISSUES:")
            for issue in analysis["issues"]:
                lines.append(f"     • {issue}")
            lines.append("")

        if analysis["warnings"]:
            lines.append("  🟡 WARNINGS:")
            for warn in analysis["warnings"]:
                lines.append(f"     • {warn}")
            lines.append("")

    return "\n".join(lines)
