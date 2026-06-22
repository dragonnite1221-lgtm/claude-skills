# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from budget_variance_analyzer_base import *  # noqa: F403,E402


class BudgetVarianceAnalyzerMixin3:
    def format_text(self, results: Dict[str, Any]) -> str:
        """Format results as human-readable text."""
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("BUDGET VARIANCE ANALYSIS")
        lines.append("=" * 70)

        summary = results["executive_summary"]
        lines.append(f"\n  Company: {summary['company']}")
        lines.append(f"  Period:  {summary['period']}")

        def fmt_money(val: float) -> str:
            sign = "+" if val > 0 else ""
            if abs(val) >= 1e6:
                return f"{sign}${val / 1e6:,.2f}M"
            if abs(val) >= 1e3:
                return f"{sign}${val / 1e3:,.1f}K"
            return f"{sign}${val:,.2f}"

        lines.append(f"\n--- EXECUTIVE SUMMARY ---")
        rev = summary["revenue"]
        exp = summary["expenses"]
        lines.append(
            f"  Revenue:  Actual {fmt_money(rev['actual'])} vs "
            f"Budget {fmt_money(rev['budget'])} "
            f"({fmt_money(rev['variance_amount'])}, {rev['variance_pct']:+.1f}%)"
        )
        lines.append(
            f"  Expenses: Actual {fmt_money(exp['actual'])} vs "
            f"Budget {fmt_money(exp['budget'])} "
            f"({fmt_money(exp['variance_amount'])}, {exp['variance_pct']:+.1f}%)"
        )
        lines.append(f"  Net Impact: {fmt_money(summary['net_impact'])}")
        lines.append(
            f"  Total Items: {summary['total_line_items']}  |  "
            f"Material: {summary['material_variances_count']}  |  "
            f"Favorable: {summary['favorable_count']}  |  "
            f"Unfavorable: {summary['unfavorable_count']}"
        )

        # Material variances
        material = results["material_variances"]
        if material:
            lines.append(f"\n--- MATERIAL VARIANCES ---")
            lines.append(
                f"  (Threshold: {self.threshold_pct}% or "
                f"${self.threshold_amt:,.0f})"
            )
            for v in material:
                lines.append(
                    f"\n  {v['name']} ({v['department']})"
                )
                lines.append(
                    f"    Actual: {fmt_money(v['actual'])} | "
                    f"Budget: {fmt_money(v['budget'])}"
                )
                lines.append(
                    f"    Variance: {fmt_money(v['budget_variance_amount'])} "
                    f"({v['budget_variance_pct']:+.1f}%) - {v['favorability']}"
                )

        # Department summary
        dept = results["department_summary"]
        if dept:
            lines.append(f"\n--- DEPARTMENT SUMMARY ---")
            for dept_name, d in dept.items():
                lines.append(
                    f"  {dept_name}: Variance {fmt_money(d['total_variance'])} "
                    f"({d['variance_pct']:+.1f}%) | "
                    f"Fav: {d['favorable_count']} / Unfav: {d['unfavorable_count']}"
                )

        # Category summary
        cat = results["category_summary"]
        if cat:
            lines.append(f"\n--- CATEGORY SUMMARY ---")
            for cat_name, c in cat.items():
                lines.append(
                    f"  {cat_name}: Variance {fmt_money(c['total_variance'])} "
                    f"({c['variance_pct']:+.1f}%)"
                )

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
