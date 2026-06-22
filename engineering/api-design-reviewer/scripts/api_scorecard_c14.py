# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin14:
    def generate_json_report(self) -> str:
        """Generate JSON format scorecard."""
        report_data = {
            "overall": {
                "score": round(self.scorecard.overall_score, 2),
                "grade": self.scorecard.overall_grade,
                "totalEndpoints": self.scorecard.total_endpoints
            },
            "api_info": self.scorecard.api_info,
            "categories": {},
            "topRecommendations": self.scorecard.get_top_recommendations()
        }
        
        for category, score in self.scorecard.category_scores.items():
            report_data["categories"][category.value] = {
                "score": round(score.score, 2),
                "grade": score.letter_grade,
                "weight": score.weight,
                "weightedScore": round(score.weighted_score, 2),
                "issues": score.issues,
                "recommendations": score.recommendations
            }
        
        return json.dumps(report_data, indent=2)
