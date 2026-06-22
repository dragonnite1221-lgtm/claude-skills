# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class ScoreCategory(Enum):
    """Scoring categories."""
    CONSISTENCY = "consistency"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    USABILITY = "usability"
    PERFORMANCE = "performance"


@dataclass
class CategoryScore:
    """Score for a specific category."""
    category: ScoreCategory
    score: float  # 0-100
    max_score: float  # Usually 100
    weight: float  # Percentage weight in overall score
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def letter_grade(self) -> str:
        """Convert score to letter grade."""
        if self.score >= 90:
            return "A"
        elif self.score >= 80:
            return "B"
        elif self.score >= 70:
            return "C"
        elif self.score >= 60:
            return "D"
        else:
            return "F"
    
    @property
    def weighted_score(self) -> float:
        """Calculate weighted contribution to overall score."""
        return (self.score / 100.0) * self.weight


@dataclass
class APIScorecard:
    """Complete API scorecard with all category scores."""
    category_scores: Dict[ScoreCategory, CategoryScore] = field(default_factory=dict)
    overall_score: float = 0.0
    overall_grade: str = "F"
    total_endpoints: int = 0
    api_info: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_overall_score(self) -> None:
        """Calculate overall weighted score and grade."""
        self.overall_score = sum(score.weighted_score for score in self.category_scores.values())
        
        if self.overall_score >= 90:
            self.overall_grade = "A"
        elif self.overall_score >= 80:
            self.overall_grade = "B"
        elif self.overall_score >= 70:
            self.overall_grade = "C"
        elif self.overall_score >= 60:
            self.overall_grade = "D"
        else:
            self.overall_grade = "F"
    
    def get_top_recommendations(self, limit: int = 5) -> List[str]:
        """Get top recommendations across all categories."""
        all_recommendations = []
        for category_score in self.category_scores.values():
            for rec in category_score.recommendations:
                all_recommendations.append(f"{category_score.category.value.title()}: {rec}")
        
        # Sort by category weight (highest impact first)
        weighted_recs = []
        for category_score in sorted(self.category_scores.values(), 
                                   key=lambda x: x.weight, reverse=True):
            for rec in category_score.recommendations[:2]:  # Top 2 per category
                weighted_recs.append(f"{category_score.category.value.title()}: {rec}")
        
        return weighted_recs[:limit]
