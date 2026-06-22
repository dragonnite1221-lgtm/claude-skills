# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402


class DebtPrioritizerMixin4:
    def _calculate_wsjf_score(self, item: Dict[str, Any]) -> float:
        """Calculate priority score using Weighted Shortest Job First (WSJF)."""
        business_impact = item["business_impact"]
        effort = item["effort_estimate"]
        
        # Business value
        business_value = (
            business_impact["customer_impact"] * 0.4 +
            business_impact["revenue_impact"] * 0.6
        )
        
        # Time criticality
        time_criticality = item["cost_of_delay"] / 10  # Normalize
        time_criticality = min(10, max(1, time_criticality))
        
        # Risk reduction
        risk_reduction = (
            business_impact["security_impact"] * 0.5 +
            business_impact["quality_impact"] * 0.5
        )
        
        # Job size (effort)
        job_size = effort["size_points"]
        
        # WSJF calculation
        numerator = business_value + time_criticality + risk_reduction
        denominator = max(1, job_size)
        
        return round(numerator / denominator, 2)
    def _calculate_rice_score(self, item: Dict[str, Any]) -> float:
        """Calculate priority score using RICE framework."""
        business_impact = item["business_impact"]
        effort = item["effort_estimate"]
        
        # Reach (how many developers/users affected)
        reach = min(10, self.team_size * business_impact["team_velocity_impact"] / 5)
        
        # Impact
        impact = (
            business_impact["customer_impact"] * 0.3 +
            business_impact["revenue_impact"] * 0.3 +
            business_impact["quality_impact"] * 0.4
        )
        
        # Confidence
        confidence = effort["confidence"] * 10
        
        # Effort
        effort_score = effort["size_points"]
        
        # RICE calculation
        rice_score = (reach * impact * confidence) / max(1, effort_score)
        
        return round(rice_score, 2)
    def _generate_sprint_allocation(self) -> Dict[str, Any]:
        """Generate sprint allocation recommendations."""
        # Calculate total effort needed
        total_effort_hours = sum(item["effort_estimate"]["hours_estimate"] 
                               for item in self.prioritized_items)
        
        # Assume 20% of sprint capacity goes to tech debt
        debt_capacity_per_sprint = self.sprint_capacity_hours * 0.2
        
        # Allocate items to sprints
        sprints = []
        current_sprint = {"sprint_number": 1, "items": [], "total_hours": 0, "capacity_used": 0}
        
        for item in self.prioritized_items:
            item_effort = item["effort_estimate"]["hours_estimate"]
            
            if current_sprint["total_hours"] + item_effort <= debt_capacity_per_sprint:
                current_sprint["items"].append(item)
                current_sprint["total_hours"] += item_effort
                current_sprint["capacity_used"] = current_sprint["total_hours"] / debt_capacity_per_sprint
            else:
                # Start new sprint
                sprints.append(current_sprint)
                current_sprint = {
                    "sprint_number": len(sprints) + 1,
                    "items": [item],
                    "total_hours": item_effort,
                    "capacity_used": item_effort / debt_capacity_per_sprint
                }
        
        # Add the last sprint
        if current_sprint["items"]:
            sprints.append(current_sprint)
        
        # Calculate summary statistics
        total_sprints_needed = len(sprints)
        high_priority_items = len([item for item in self.prioritized_items 
                                 if item.get("priority", "medium") in ["high", "critical"]])
        
        return {
            "total_debt_hours": round(total_effort_hours, 1),
            "debt_capacity_per_sprint": debt_capacity_per_sprint,
            "total_sprints_needed": total_sprints_needed,
            "high_priority_items": high_priority_items,
            "sprint_plan": sprints[:6],  # Show first 6 sprints
            "recommendations": [
                f"Allocate {debt_capacity_per_sprint} hours per sprint to tech debt",
                f"Focus on {high_priority_items} high-priority items first",
                f"Estimated {total_sprints_needed} sprints to clear current backlog"
            ]
        }
