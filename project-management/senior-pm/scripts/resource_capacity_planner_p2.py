# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from resource_capacity_planner_base import *  # noqa: F403,E402
# fmt: off
from resource_capacity_planner_p1 import CAPACITY_FACTORS, PROJECT_COMPLEXITY_FACTORS, ROLE_TYPES  # noqa: E402,E501
# fmt: on


class Resource:
    """Represents a team member with skills and capacity."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.role: str = data.get("role", "").lower()
        self.skills: List[str] = data.get("skills", [])
        self.skill_levels: Dict[str, float] = data.get("skill_levels", {})
        self.hourly_rate: float = data.get("hourly_rate", 0)
        self.max_hours_per_week: int = data.get("max_hours_per_week", 40)
        self.current_utilization: float = data.get("current_utilization", 0.0)
        self.availability_start: str = data.get("availability_start", "")
        self.availability_end: Optional[str] = data.get("availability_end")
        self.location: str = data.get("location", "")
        self.time_zone: str = data.get("time_zone", "")
        
        # Calculate derived metrics
        self._calculate_effective_capacity()
        self._determine_role_config()
    
    def _calculate_effective_capacity(self):
        """Calculate effective weekly capacity accounting for overhead."""
        base_capacity = self.max_hours_per_week
        
        # Apply overhead factors
        overhead_total = sum(CAPACITY_FACTORS.values())
        self.effective_hours_per_week = base_capacity * (1 - overhead_total)
        
        # Current available capacity
        self.available_hours = self.effective_hours_per_week * (1 - self.current_utilization)
    
    def _determine_role_config(self):
        """Get role configuration from predefined types."""
        self.role_config = ROLE_TYPES.get(self.role, {
            "hourly_rate": self.hourly_rate or 100,
            "efficiency_factor": 1.0,
            "skill_multipliers": {}
        })
        
        # Use provided rate if available, otherwise use role default
        if not self.hourly_rate:
            self.hourly_rate = self.role_config["hourly_rate"]
    
    def get_skill_effectiveness(self, skill: str) -> float:
        """Calculate effectiveness for a specific skill."""
        base_level = self.skill_levels.get(skill, 0.5)  # Default 50% if not specified
        multiplier = self.role_config.get("skill_multipliers", {}).get(skill, 1.0)
        efficiency = self.role_config.get("efficiency_factor", 1.0)
        
        return base_level * multiplier * efficiency
    
    def can_work_on_project(self, project_skills: List[str], min_effectiveness: float = 0.6) -> bool:
        """Check if resource can effectively work on project."""
        for skill in project_skills:
            if skill in self.skills and self.get_skill_effectiveness(skill) >= min_effectiveness:
                return True
        return False
class Project:
    """Represents a project with resource requirements."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.priority: str = data.get("priority", "medium").lower()
        self.complexity: str = data.get("complexity", "moderate").lower()
        self.estimated_hours: int = data.get("estimated_hours", 0)
        self.start_date: str = data.get("start_date", "")
        self.target_end_date: str = data.get("target_end_date", "")
        self.required_skills: List[str] = data.get("required_skills", [])
        self.skill_requirements: Dict[str, int] = data.get("skill_requirements", {})
        self.current_allocation: List[Dict[str, Any]] = data.get("current_allocation", [])
        self.status: str = data.get("status", "planned").lower()
        
        # Calculate derived metrics
        self._calculate_project_metrics()
    
    def _calculate_project_metrics(self):
        """Calculate project-specific metrics."""
        # Apply complexity factor
        complexity_multiplier = PROJECT_COMPLEXITY_FACTORS.get(self.complexity, 1.0)
        self.adjusted_hours = self.estimated_hours * complexity_multiplier
        
        # Calculate current allocation
        self.currently_allocated_hours = sum(
            alloc.get("hours_per_week", 0) for alloc in self.current_allocation
        )
        
        # Calculate timeline metrics
        if self.start_date and self.target_end_date:
            try:
                start = datetime.strptime(self.start_date, "%Y-%m-%d")
                end = datetime.strptime(self.target_end_date, "%Y-%m-%d")
                self.duration_weeks = (end - start).days / 7
                
                # Required weekly capacity
                if self.duration_weeks > 0:
                    self.required_hours_per_week = self.adjusted_hours / self.duration_weeks
                else:
                    self.required_hours_per_week = self.adjusted_hours
            except ValueError:
                self.duration_weeks = 0
                self.required_hours_per_week = 0
        else:
            self.duration_weeks = 0
            self.required_hours_per_week = 0
        
        # Capacity gap
        self.capacity_gap = self.required_hours_per_week - self.currently_allocated_hours
class CapacityAnalysisResult:
    """Complete capacity analysis results."""
    
    def __init__(self):
        self.summary: Dict[str, Any] = {}
        self.resource_analysis: Dict[str, Any] = {}
        self.project_analysis: Dict[str, Any] = {}
        self.allocation_optimization: Dict[str, Any] = {}
        self.scenario_analysis: Dict[str, Any] = {}
        self.recommendations: List[str] = []
