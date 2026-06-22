# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402


class DebtPrioritizerMixin0:
    """Main class for prioritizing technical debt items."""
    def __init__(self, team_size: int = 5, sprint_capacity_hours: int = 80):
        self.team_size = team_size
        self.sprint_capacity_hours = sprint_capacity_hours
        self.debt_items = []
        self.prioritized_items = []
        
        # Prioritization framework weights
        self.framework_weights = {
            "cost_of_delay": {
                "business_value": 0.3,
                "urgency": 0.3,
                "risk_reduction": 0.2,
                "team_productivity": 0.2
            },
            "wsjf": {
                "business_value": 0.25,
                "time_criticality": 0.25,
                "risk_reduction": 0.25,
                "effort": 0.25
            },
            "rice": {
                "reach": 0.25,
                "impact": 0.25,
                "confidence": 0.25,
                "effort": 0.25
            }
        }
    def load_debt_inventory(self, file_path: str) -> bool:
        """Load debt inventory from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different input formats
            if isinstance(data, dict) and 'debt_items' in data:
                self.debt_items = data['debt_items']
            elif isinstance(data, list):
                self.debt_items = data
            else:
                raise ValueError("Invalid debt inventory format")
            
            print(f"Loaded {len(self.debt_items)} debt items from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading debt inventory: {e}")
            return False
    def analyze_and_prioritize(self, framework: str = "cost_of_delay") -> Dict[str, Any]:
        """
        Analyze debt items and create prioritized backlog.
        
        Args:
            framework: Prioritization framework to use
            
        Returns:
            Dictionary containing prioritized backlog and analysis
        """
        print(f"Analyzing {len(self.debt_items)} debt items...")
        print(f"Using {framework} prioritization framework")
        print("=" * 50)
        
        # Step 1: Enrich debt items with estimates
        enriched_items = []
        for item in self.debt_items:
            enriched_item = self._enrich_debt_item(item)
            enriched_items.append(enriched_item)
        
        # Step 2: Calculate prioritization scores
        for item in enriched_items:
            if framework == "cost_of_delay":
                item["priority_score"] = self._calculate_cost_of_delay_score(item)
            elif framework == "wsjf":
                item["priority_score"] = self._calculate_wsjf_score(item)
            elif framework == "rice":
                item["priority_score"] = self._calculate_rice_score(item)
            else:
                raise ValueError(f"Unknown prioritization framework: {framework}")
        
        # Step 3: Sort by priority score
        self.prioritized_items = sorted(enriched_items, 
                                      key=lambda x: x["priority_score"], 
                                      reverse=True)
        
        # Step 4: Generate sprint allocation recommendations
        sprint_allocation = self._generate_sprint_allocation()
        
        # Step 5: Generate insights and recommendations
        insights = self._generate_insights()
        
        # Step 6: Create visualization data
        charts_data = self._generate_charts_data()
        
        return {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "framework_used": framework,
                "team_size": self.team_size,
                "sprint_capacity_hours": self.sprint_capacity_hours,
                "total_items_analyzed": len(self.debt_items)
            },
            "prioritized_backlog": self.prioritized_items,
            "sprint_allocation": sprint_allocation,
            "insights": insights,
            "charts_data": charts_data,
            "recommendations": self._generate_recommendations()
        }
