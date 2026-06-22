# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from output_analyzer_base import *  # noqa: F403,E402
# fmt: off
from output_analyzer_p1 import get_nested  # noqa: E402,E501
# fmt: on


def compute_stats(records: List[Dict], field: str) -> Dict[str, Any]:
    """Compute min/max/avg/sum for a numeric field."""
    values = []
    for rec in records:
        val = get_nested(rec, field)
        if val is not None:
            try:
                values.append(float(val))
            except (ValueError, TypeError):
                continue
    if not values:
        return {"field": field, "count": 0, "error": "No numeric values found"}
    return {
        "field": field,
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "sum": sum(values),
        "avg": sum(values) / len(values),
    }
def format_table(records: List[Dict]) -> str:
    """Format records as an aligned text table."""
    if not records:
        return "(no records)"

    headers = list(records[0].keys())
    # Calculate column widths
    widths = {h: len(h) for h in headers}
    for rec in records:
        for h in headers:
            val = str(rec.get(h, ""))
            if len(val) > 60:
                val = val[:57] + "..."
            widths[h] = max(widths[h], len(val))

    # Header
    header_line = "  ".join(h.ljust(widths[h]) for h in headers)
    sep_line = "  ".join("-" * widths[h] for h in headers)
    lines = [header_line, sep_line]

    # Rows
    for rec in records:
        row = []
        for h in headers:
            val = str(rec.get(h, ""))
            if len(val) > 60:
                val = val[:57] + "..."
            row.append(val.ljust(widths[h]))
        lines.append("  ".join(row))

    return "\n".join(lines)
def format_csv_output(records: List[Dict]) -> str:
    """Format records as CSV."""
    if not records:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()
