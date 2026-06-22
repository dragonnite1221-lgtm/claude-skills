# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from query_optimizer_base import *  # noqa: F403,E402
# fmt: off
from query_optimizer_p1 import Issue, QueryAnalysis, check_cartesian_join, check_function_on_column, check_leading_wildcard, check_missing_limit, check_missing_where, check_select_star, check_subquery_in_select  # noqa: E402,E501
# fmt: on


def check_order_by_rand(sql: str) -> Optional[Issue]:
    """Detect ORDER BY RAND() / RANDOM()."""
    if re.search(r'ORDER\s+BY\s+(RAND|RANDOM)\s*\(\)', sql, re.IGNORECASE):
        return Issue(
            severity="warning",
            rule="order-by-rand",
            message="ORDER BY RAND() scans and sorts the entire table.",
            suggestion="Use application-side random sampling or TABLESAMPLE.",
        )
    return None
def check_union_vs_union_all(sql: str) -> Optional[Issue]:
    """Detect UNION without ALL (unnecessary dedup)."""
    if re.search(r'\bUNION\b(?!\s+ALL\b)', sql, re.IGNORECASE):
        return Issue(
            severity="info",
            rule="union-without-all",
            message="UNION performs deduplication sort; use UNION ALL if duplicates are acceptable.",
            suggestion="Replace UNION with UNION ALL unless you specifically need deduplication.",
        )
    return None
def check_not_in_subquery(sql: str) -> Optional[Issue]:
    """Detect NOT IN (SELECT ...) which is NULL-unsafe."""
    if re.search(r'\bNOT\s+IN\s*\(\s*SELECT\b', sql, re.IGNORECASE):
        return Issue(
            severity="warning",
            rule="not-in-subquery",
            message="NOT IN with subquery returns no rows if any subquery result is NULL.",
            suggestion="Use NOT EXISTS (SELECT 1 ...) instead.",
        )
    return None
ALL_CHECKS = [
    check_select_star,
    check_missing_where,
    check_cartesian_join,
    check_subquery_in_select,
    check_missing_limit,
    check_function_on_column,
    check_leading_wildcard,
    check_order_by_rand,
    check_union_vs_union_all,
    check_not_in_subquery,
]
def analyze_query(sql: str, dialect: str = "postgres") -> QueryAnalysis:
    """Run all checks against a single SQL query."""
    issues: List[Issue] = []
    for check_fn in ALL_CHECKS:
        issue = check_fn(sql)
        if issue:
            issues.append(issue)

    # Score: start at 100, deduct per severity
    score = 100
    for issue in issues:
        if issue.severity == "critical":
            score -= 25
        elif issue.severity == "warning":
            score -= 10
        else:
            score -= 5
    score = max(0, score)

    return QueryAnalysis(query=sql.strip(), issues=issues, score=score)
def split_queries(text: str) -> List[str]:
    """Split SQL text into individual statements."""
    queries = []
    for stmt in text.split(";"):
        stmt = stmt.strip()
        if stmt and len(stmt) > 5:
            queries.append(stmt + ";")
    return queries
SEVERITY_ICONS = {"critical": "[CRITICAL]", "warning": "[WARNING]", "info": "[INFO]"}
def format_text(analyses: List[QueryAnalysis]) -> str:
    """Format analysis results as human-readable text."""
    lines = []
    for i, analysis in enumerate(analyses, 1):
        lines.append(f"{'='*60}")
        lines.append(f"Query {i} (Score: {analysis.score}/100)")
        lines.append(f"  {analysis.query[:120]}{'...' if len(analysis.query) > 120 else ''}")
        lines.append("")
        if not analysis.issues:
            lines.append("  No issues detected.")
        for issue in analysis.issues:
            icon = SEVERITY_ICONS.get(issue.severity, "")
            lines.append(f"  {icon} {issue.rule}: {issue.message}")
            lines.append(f"    -> {issue.suggestion}")
        lines.append("")
    return "\n".join(lines)
def format_json(analyses: List[QueryAnalysis]) -> str:
    """Format analysis results as JSON."""
    return json.dumps(
        {"analyses": [a.to_dict() for a in analyses], "total_queries": len(analyses)},
        indent=2,
    )
