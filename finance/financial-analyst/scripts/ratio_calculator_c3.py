# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ratio_calculator_base import *  # noqa: F403,E402


class FinancialRatioCalculatorMixin3:
    @staticmethod
    def format_ratio(value: float, is_percentage: bool = False) -> str:
        """Format a ratio value for display."""
        if is_percentage:
            return f"{value * 100:.1f}%"
        return f"{value:.2f}"
    def format_text(self, category: Optional[str] = None) -> str:
        """Format results as human-readable text."""
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("FINANCIAL RATIO ANALYSIS")
        lines.append("=" * 70)

        categories = (
            {category: self.results[category]}
            if category and category in self.results
            else self.results
        )

        percentage_ratios = {
            "roe", "roa", "gross_margin", "operating_margin", "net_margin"
        }

        for cat_name, ratios in categories.items():
            lines.append(f"\n--- {cat_name.upper()} ---")
            for key, ratio in ratios.items():
                is_pct = key in percentage_ratios
                formatted = self.format_ratio(ratio["value"], is_pct)
                lines.append(f"  {ratio['name']}: {formatted}")
                lines.append(f"    Formula: {ratio['formula']}")
                lines.append(f"    Assessment: {ratio['interpretation']}")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)
    def to_json(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Return results as JSON-serializable dict."""
        if category and category in self.results:
            return {"category": category, "ratios": self.results[category]}
        return {"categories": self.results}
