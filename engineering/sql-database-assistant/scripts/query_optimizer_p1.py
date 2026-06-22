# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from query_optimizer_base import *  # noqa: F403,E402


@dataclass
class Issue:
    """A single optimization issue found in a query."""
    severity: str  # critical, warning, info
    rule: str
    message: str
    suggestion: str
    line: Optional[int] = None
@dataclass
class QueryAnalysis:
    """Analysis result for one SQL query."""
    query: str
    issues: List[Issue]
    score: int  # 0-100, higher is better

    def to_dict(self):
        return {
            "query": self.query[:200] + ("..." if len(self.query) > 200 else ""),
            "issues": [asdict(i) for i in self.issues],
            "issue_count": len(self.issues),
            "score": self.score,
        }
def check_select_star(sql: str) -> Optional[Issue]:
    """Detect SELECT * usage."""
    if re.search(r'\bSELECT\s+\*\s', sql, re.IGNORECASE):
        return Issue(
            severity="warning",
            rule="select-star",
            message="SELECT * transfers unnecessary data and breaks on schema changes.",
            suggestion="List only the columns you need: SELECT col1, col2, ...",
        )
    return None
def check_missing_where(sql: str) -> Optional[Issue]:
    """Detect UPDATE/DELETE without WHERE."""
    upper = sql.upper().strip()
    for keyword in ("UPDATE", "DELETE"):
        if upper.startswith(keyword) and "WHERE" not in upper:
            return Issue(
                severity="critical",
                rule="missing-where",
                message=f"{keyword} without WHERE affects every row in the table.",
                suggestion=f"Add a WHERE clause to restrict the {keyword} scope.",
            )
    return None
def check_cartesian_join(sql: str) -> Optional[Issue]:
    """Detect comma-separated tables without explicit JOIN or WHERE join condition."""
    upper = sql.upper()
    if "SELECT" not in upper:
        return None
    from_match = re.search(r'\bFROM\s+(.+?)(?:\bWHERE\b|\bGROUP\b|\bORDER\b|\bLIMIT\b|\bHAVING\b|;|$)',
                           sql, re.IGNORECASE | re.DOTALL)
    if not from_match:
        return None
    from_clause = from_match.group(1)
    # Skip if explicit JOINs are used
    if re.search(r'\bJOIN\b', from_clause, re.IGNORECASE):
        return None
    # Count comma-separated tables
    tables = [t.strip() for t in from_clause.split(",") if t.strip()]
    if len(tables) > 1 and "WHERE" not in upper:
        return Issue(
            severity="critical",
            rule="cartesian-join",
            message="Multiple tables in FROM without JOIN or WHERE creates a cartesian product.",
            suggestion="Use explicit JOIN syntax with ON conditions.",
        )
    return None
def check_subquery_in_select(sql: str) -> Optional[Issue]:
    """Detect correlated subqueries in SELECT list."""
    select_match = re.search(r'\bSELECT\b(.+?)\bFROM\b', sql, re.IGNORECASE | re.DOTALL)
    if select_match:
        select_clause = select_match.group(1)
        if re.search(r'\(\s*SELECT\b', select_clause, re.IGNORECASE):
            return Issue(
                severity="warning",
                rule="subquery-in-select",
                message="Subquery in SELECT list executes once per row (correlated subquery).",
                suggestion="Rewrite as a LEFT JOIN with aggregation.",
            )
    return None
def check_missing_limit(sql: str) -> Optional[Issue]:
    """Detect unbounded SELECT without LIMIT."""
    upper = sql.upper().strip()
    if not upper.startswith("SELECT"):
        return None
    # Skip if it's a subquery or aggregate-only
    if re.search(r'\bCOUNT\s*\(', upper) and "GROUP BY" not in upper:
        return None
    if "LIMIT" not in upper and "FETCH" not in upper and "TOP " not in upper:
        return Issue(
            severity="info",
            rule="missing-limit",
            message="SELECT without LIMIT may return unbounded rows.",
            suggestion="Add LIMIT to prevent returning excessive data.",
        )
    return None
def check_function_on_column(sql: str) -> Optional[Issue]:
    """Detect function calls on columns in WHERE (non-sargable)."""
    where_match = re.search(r'\bWHERE\b(.+?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|\bHAVING\b|;|$)',
                            sql, re.IGNORECASE | re.DOTALL)
    if not where_match:
        return None
    where_clause = where_match.group(1)
    non_sargable = re.search(
        r'\b(YEAR|MONTH|DAY|DATE|UPPER|LOWER|TRIM|CAST|COALESCE|IFNULL|NVL)\s*\(',
        where_clause, re.IGNORECASE
    )
    if non_sargable:
        func = non_sargable.group(1).upper()
        return Issue(
            severity="warning",
            rule="non-sargable",
            message=f"Function {func}() on column in WHERE prevents index usage.",
            suggestion="Rewrite to compare the raw column against transformed constants.",
        )
    return None
def check_leading_wildcard(sql: str) -> Optional[Issue]:
    """Detect LIKE '%...' patterns."""
    if re.search(r"LIKE\s+'%", sql, re.IGNORECASE):
        return Issue(
            severity="warning",
            rule="leading-wildcard",
            message="LIKE with leading wildcard prevents index usage.",
            suggestion="Use full-text search (GIN index, FULLTEXT, FTS5) for substring matching.",
        )
    return None
