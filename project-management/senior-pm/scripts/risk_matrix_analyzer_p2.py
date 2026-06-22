# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_analyzer_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_analyzer_p1 import RISK_CATEGORIES, RISK_TOLERANCE_THRESHOLDS  # noqa: E402,E501
# fmt: on


class Risk:
    """Represents a single project risk with assessment and mitigation data."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.title: str = data.get("title", "")
        self.description: str = data.get("description", "")
        self.category: str = data.get("category", "technical").lower()
        self.probability: int = max(1, min(5, data.get("probability", 3)))
        self.impact: int = max(1, min(5, data.get("impact", 3)))
        self.owner: str = data.get("owner", "")
        self.status: str = data.get("status", "open").lower()
        self.identified_date: str = data.get("identified_date", "")
        self.target_resolution: Optional[str] = data.get("target_resolution")
        self.mitigation_strategy: str = data.get("mitigation_strategy", "").lower()
        self.mitigation_actions: List[str] = data.get("mitigation_actions", [])
        self.cost_impact: Optional[float] = data.get("cost_impact")
        self.schedule_impact: Optional[int] = data.get("schedule_impact_days")
        
        # Calculate derived metrics
        self._calculate_risk_score()
        self._determine_risk_level()
        self._suggest_mitigation_approach()
    
    def _calculate_risk_score(self):
        """Calculate weighted risk score based on category, probability, and impact."""
        base_score = self.probability * self.impact
        category_weight = RISK_CATEGORIES.get(self.category, {}).get("weight", 1.0)
        self.risk_score = base_score * category_weight
    
    def _determine_risk_level(self):
        """Determine risk level based on score thresholds."""
        if self.risk_score <= RISK_TOLERANCE_THRESHOLDS["low"]:
            self.risk_level = "low"
        elif self.risk_score <= RISK_TOLERANCE_THRESHOLDS["medium"]:
            self.risk_level = "medium"
        elif self.risk_score <= RISK_TOLERANCE_THRESHOLDS["high"]:
            self.risk_level = "high"
        else:
            self.risk_level = "critical"
    
    def _suggest_mitigation_approach(self):
        """Suggest mitigation approach based on risk characteristics."""
        if self.risk_level == "low":
            self.suggested_approach = "accept"
        elif self.probability >= 4 and self.impact <= 2:
            self.suggested_approach = "mitigate"  # Likely but low impact
        elif self.probability <= 2 and self.impact >= 4:
            self.suggested_approach = "contingency"  # Unlikely but high impact
        elif self.impact >= 4:
            self.suggested_approach = "avoid"  # High impact risks
        else:
            self.suggested_approach = "mitigate"
    
    @property
    def is_active(self) -> bool:
        return self.status.lower() in ["open", "identified", "monitoring", "mitigating"]
    
    @property
    def is_overdue(self) -> bool:
        if not self.target_resolution:
            return False
        
        try:
            target_date = datetime.strptime(self.target_resolution, "%Y-%m-%d")
            return datetime.now() > target_date and self.is_active
        except ValueError:
            return False
class RiskAnalysisResult:
    """Complete risk analysis results."""
    
    def __init__(self):
        self.summary: Dict[str, Any] = {}
        self.risk_matrix: Dict[str, Any] = {}
        self.category_analysis: Dict[str, Any] = {}
        self.mitigation_analysis: Dict[str, Any] = {}
        self.trend_analysis: Dict[str, Any] = {}
        self.recommendations: List[str] = []
def _classify_risk_exposure(average_score: float) -> str:
    """Classify overall portfolio risk exposure level."""
    if average_score > 18:
        return "very_high"
    elif average_score > 15:
        return "high"
    elif average_score > 12:
        return "medium"
    elif average_score > 8:
        return "low"
    else:
        return "very_low"
