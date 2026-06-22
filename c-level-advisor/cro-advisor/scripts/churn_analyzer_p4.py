# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402


class ExpansionAnalyzer:
    def __init__(self, customers):
        self.customers = customers

    def expansion_summary(self):
        active = [c for c in self.customers if not c.is_churned()]
        expanding = [c for c in active if c.expansion_arr > 0]
        contracting = [c for c in active if c.contraction_arr > 0]

        total_arr = sum(c.arr for c in active)
        total_expansion = sum(c.expansion_arr for c in active)
        total_contraction = sum(c.contraction_arr for c in active)

        return {
            "active_customers":   len(active),
            "total_arr":          total_arr,
            "expanding_count":    len(expanding),
            "contracting_count":  len(contracting),
            "expansion_arr":      total_expansion,
            "contraction_arr":    total_contraction,
            "expansion_rate":     total_expansion / total_arr if total_arr else 0,
            "contraction_rate":   total_contraction / total_arr if total_arr else 0,
            "net_expansion_rate": (total_expansion - total_contraction) / total_arr if total_arr else 0,
        }

    def expansion_by_segment(self):
        active = [c for c in self.customers if not c.is_churned()]
        by_segment = defaultdict(lambda: {"arr": 0.0, "expansion": 0.0,
                                          "contraction": 0.0, "count": 0})
        for c in active:
            seg = c.segment or "Unspecified"
            by_segment[seg]["arr"] += c.arr
            by_segment[seg]["expansion"] += c.expansion_arr
            by_segment[seg]["contraction"] += c.contraction_arr
            by_segment[seg]["count"] += 1

        result = {}
        for seg, data in by_segment.items():
            arr = data["arr"]
            result[seg] = {
                "customer_count":  data["count"],
                "arr":             arr,
                "expansion_arr":   data["expansion"],
                "contraction_arr": data["contraction"],
                "expansion_rate":  data["expansion"] / arr if arr else 0,
                "net_nrr_contribution": (arr + data["expansion"] - data["contraction"]) / arr if arr else 0,
            }
        return result

    def top_expansion_candidates(self, min_tenure_months=6, min_arr=5000):
        """
        Customers who are active, healthy tenure, but have zero expansion.
        These are upsell/expansion targets.
        """
        active = [c for c in self.customers if not c.is_churned()]
        candidates = []
        for c in active:
            tenure = c.tenure_months()
            if (tenure >= min_tenure_months
                    and c.arr >= min_arr
                    and c.expansion_arr == 0
                    and (c.health_score is None or c.health_score >= 60)):
                candidates.append({
                    "customer_id":   c.customer_id,
                    "name":          c.name,
                    "segment":       c.segment,
                    "arr":           c.arr,
                    "tenure_months": round(tenure, 1),
                    "health_score":  c.health_score,
                })
        return sorted(candidates, key=lambda x: -x["arr"])
def fmt_currency(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"
def fmt_pct(value):
    return f"{value * 100:.1f}%"
def nrr_status(nrr):
    if nrr >= 1.20:
        return "✅ World-class"
    if nrr >= 1.10:
        return "✅ Healthy"
    if nrr >= 1.00:
        return "⚠️  Acceptable"
    if nrr >= 0.90:
        return "🔴 Concerning"
    return "🔴 Crisis"
def grr_status(grr):
    if grr >= 0.90:
        return "✅ Strong"
    if grr >= 0.85:
        return "⚠️  Acceptable"
    return "🔴 Below threshold"
def print_header(title):
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
def print_section(title):
    print(f"\n--- {title} ---")
