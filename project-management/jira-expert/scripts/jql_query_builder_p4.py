# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from jql_query_builder_base import *  # noqa: F403,E402
# fmt: off
from jql_query_builder_p1 import PATTERN_LIBRARY  # noqa: E402,E501
# fmt: on


def validate_jql_syntax(jql: str) -> Dict[str, Any]:
    """Basic JQL syntax validation."""
    issues = []

    if not jql.strip():
        return {"valid": False, "issues": ["Empty query"]}

    # Check balanced quotes
    single_quotes = jql.count("'")
    double_quotes = jql.count('"')
    if single_quotes % 2 != 0:
        issues.append("Unbalanced single quotes")
    if double_quotes % 2 != 0:
        issues.append("Unbalanced double quotes")

    # Check balanced parentheses
    open_parens = jql.count("(")
    close_parens = jql.count(")")
    if open_parens != close_parens:
        issues.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")

    # Check for known JQL operators
    valid_operators = {"=", "!=", ">", "<", ">=", "<=", "~", "!~", "in", "not in", "is", "is not", "was", "was not", "changed"}
    jql_upper = jql.upper()

    # Check AND/OR placement
    if jql_upper.strip().startswith("AND") or jql_upper.strip().startswith("OR"):
        issues.append("Query cannot start with AND/OR")
    if jql_upper.strip().endswith("AND") or jql_upper.strip().endswith("OR"):
        issues.append("Query cannot end with AND/OR")

    # Check ORDER BY syntax
    order_match = re.search(r'ORDER\s+BY\s+(\w+)(?:\s+(ASC|DESC))?', jql, re.IGNORECASE)
    if "ORDER" in jql_upper and not order_match:
        issues.append("Invalid ORDER BY syntax")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "query_length": len(jql),
    }
def format_text_output(result: Dict[str, Any]) -> str:
    """Format results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("JQL QUERY BUILDER RESULTS")
    lines.append("=" * 60)
    lines.append("")

    if "error" in result:
        lines.append(f"ERROR: {result['error']}")
        return "\n".join(lines)

    lines.append(f"Match Type: {result.get('match_type', 'unknown')}")
    lines.append(f"Description: {result.get('description', '')}")
    lines.append("")
    lines.append("GENERATED JQL")
    lines.append("-" * 30)
    lines.append(result.get("jql", ""))
    lines.append("")

    validation = result.get("validation", {})
    if validation:
        lines.append("VALIDATION")
        lines.append("-" * 30)
        lines.append(f"Valid: {'Yes' if validation.get('valid') else 'No'}")
        if validation.get("issues"):
            for issue in validation["issues"]:
                lines.append(f"  - {issue}")

    if result.get("pattern_name"):
        lines.append("")
        lines.append(f"Matched Pattern: {result['pattern_name']}")

    return "\n".join(lines)
def format_patterns_output(output_format: str) -> str:
    """Format available patterns list."""
    if output_format == "json":
        patterns = {}
        for name, data in PATTERN_LIBRARY.items():
            patterns[name] = {
                "description": data["description"],
                "phrases": data["phrases"],
                "jql": data["jql"],
            }
        return json.dumps(patterns, indent=2)

    lines = []
    lines.append("=" * 60)
    lines.append("AVAILABLE JQL PATTERNS")
    lines.append("=" * 60)
    lines.append("")

    for name, data in PATTERN_LIBRARY.items():
        lines.append(f"  {name}")
        lines.append(f"    Description: {data['description']}")
        lines.append(f"    Phrases: {', '.join(data['phrases'])}")
        lines.append(f"    JQL: {data['jql']}")
        lines.append("")

    lines.append(f"Total patterns: {len(PATTERN_LIBRARY)}")
    return "\n".join(lines)
def format_json_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format results as JSON."""
    return result
