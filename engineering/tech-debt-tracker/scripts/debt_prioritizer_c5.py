# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402


class DebtPrioritizerMixin5:
    def _generate_insights(self) -> Dict[str, Any]:
        """Generate insights from the prioritized debt analysis."""
        
        # Category distribution
        categories = Counter(item["category"] for item in self.prioritized_items)
        
        # Effort distribution
        total_effort = sum(item["effort_estimate"]["hours_estimate"] 
                          for item in self.prioritized_items)
        effort_by_category = defaultdict(float)
        for item in self.prioritized_items:
            effort_by_category[item["category"]] += item["effort_estimate"]["hours_estimate"]
        
        # Priority distribution
        priorities = Counter()
        for item in self.prioritized_items:
            score = item["priority_score"]
            if score >= 8:
                priorities["critical"] += 1
            elif score >= 5:
                priorities["high"] += 1
            elif score >= 2:
                priorities["medium"] += 1
            else:
                priorities["low"] += 1
        
        # Risk analysis
        high_risk_items = [item for item in self.prioritized_items 
                          if item["effort_estimate"]["risk_factor"] >= 1.5]
        
        # Quick wins identification
        quick_wins = [item for item in self.prioritized_items 
                     if (item["effort_estimate"]["hours_estimate"] <= 8 and 
                         item["priority_score"] >= 3)]
        
        # Cost analysis
        total_cost_of_delay = sum(item["cost_of_delay"] for item in self.prioritized_items)
        avg_interest_rate = sum(item["interest_rate"]["daily_cost"] 
                              for item in self.prioritized_items) / len(self.prioritized_items)
        
        return {
            "category_distribution": dict(categories),
            "total_effort_hours": round(total_effort, 1),
            "effort_by_category": {k: round(v, 1) for k, v in effort_by_category.items()},
            "priority_distribution": dict(priorities),
            "high_risk_items_count": len(high_risk_items),
            "quick_wins_count": len(quick_wins),
            "total_cost_of_delay": round(total_cost_of_delay, 1),
            "average_daily_interest_rate": round(avg_interest_rate, 2),
            "top_categories_by_effort": sorted(effort_by_category.items(), 
                                             key=lambda x: x[1], reverse=True)[:3]
        }
    def _generate_charts_data(self) -> Dict[str, Any]:
        """Generate data for charts and visualizations."""
        
        # Priority vs Effort scatter plot data
        scatter_data = []
        for item in self.prioritized_items:
            scatter_data.append({
                "x": item["effort_estimate"]["hours_estimate"],
                "y": item["priority_score"],
                "label": item.get("description", "")[:50],
                "category": item["category"],
                "size": item["cost_of_delay"]
            })
        
        # Category effort distribution (pie chart)
        effort_by_category = defaultdict(float)
        for item in self.prioritized_items:
            effort_by_category[item["category"]] += item["effort_estimate"]["hours_estimate"]
        
        pie_data = [{"category": k, "effort": round(v, 1)} 
                   for k, v in effort_by_category.items()]
        
        # Priority timeline (bar chart)
        timeline_data = []
        cumulative_effort = 0
        for i, item in enumerate(self.prioritized_items[:20]):  # Top 20 items
            cumulative_effort += item["effort_estimate"]["hours_estimate"]
            timeline_data.append({
                "item_rank": i + 1,
                "description": item.get("description", "")[:30],
                "effort": item["effort_estimate"]["hours_estimate"],
                "cumulative_effort": round(cumulative_effort, 1),
                "priority_score": item["priority_score"]
            })
        
        # Interest rate trend (line chart data structure)
        interest_trend_data = []
        for i, item in enumerate(self.prioritized_items):
            interest_trend_data.append({
                "item_index": i,
                "daily_cost": item["interest_rate"]["daily_cost"],
                "category": item["category"]
            })
        
        return {
            "priority_effort_scatter": scatter_data,
            "category_effort_distribution": pie_data,
            "priority_timeline": timeline_data,
            "interest_rate_trend": interest_trend_data[:50]  # Limit for performance
        }
