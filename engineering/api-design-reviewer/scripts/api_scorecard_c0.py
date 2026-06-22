# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402
from api_scorecard_p0 import APIScorecard, CategoryScore, ScoreCategory  # noqa: F401,E501


class APIScoringEngineMixin0:
    """Main API scoring engine."""
    def __init__(self):
        self.scorecard = APIScorecard()
        self.spec: Optional[Dict] = None
        
        # Regex patterns for validation
        self.kebab_case_pattern = re.compile(r'^[a-z]+(?:-[a-z0-9]+)*$')
        self.camel_case_pattern = re.compile(r'^[a-z][a-zA-Z0-9]*$')
        self.pascal_case_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
        
        # HTTP methods
        self.http_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'}
        
        # Category weights (must sum to 100)
        self.category_weights = {
            ScoreCategory.CONSISTENCY: 30.0,
            ScoreCategory.DOCUMENTATION: 20.0,
            ScoreCategory.SECURITY: 20.0,
            ScoreCategory.USABILITY: 15.0,
            ScoreCategory.PERFORMANCE: 15.0
        }
    def score_api(self, spec: Dict[str, Any]) -> APIScorecard:
        """Generate comprehensive API scorecard."""
        self.spec = spec
        self.scorecard = APIScorecard()
        
        # Extract basic API info
        self._extract_api_info()
        
        # Score each category
        self._score_consistency()
        self._score_documentation()
        self._score_security()
        self._score_usability()
        self._score_performance()
        
        # Calculate overall score
        self.scorecard.calculate_overall_score()
        
        return self.scorecard
    def _extract_api_info(self) -> None:
        """Extract basic API information."""
        info = self.spec.get('info', {})
        paths = self.spec.get('paths', {})
        
        self.scorecard.api_info = {
            'title': info.get('title', 'Unknown API'),
            'version': info.get('version', ''),
            'description': info.get('description', ''),
            'total_paths': len(paths),
            'openapi_version': self.spec.get('openapi', self.spec.get('swagger', ''))
        }
        
        # Count total endpoints
        endpoint_count = 0
        for path_obj in paths.values():
            if isinstance(path_obj, dict):
                endpoint_count += len([m for m in path_obj.keys() 
                                     if m.upper() in self.http_methods])
        
        self.scorecard.total_endpoints = endpoint_count
    def _score_consistency(self) -> None:
        """Score API consistency (30% weight)."""
        category = ScoreCategory.CONSISTENCY
        score = CategoryScore(
            category=category,
            score=0.0,
            max_score=100.0,
            weight=self.category_weights[category]
        )
        
        consistency_checks = [
            self._check_naming_consistency(),
            self._check_response_consistency(),
            self._check_error_format_consistency(),
            self._check_parameter_consistency(),
            self._check_url_structure_consistency(),
            self._check_http_method_consistency(),
            self._check_status_code_consistency()
        ]
        
        # Average the consistency scores
        valid_scores = [s for s in consistency_checks if s is not None]
        if valid_scores:
            score.score = sum(valid_scores) / len(valid_scores)
        
        # Add specific recommendations based on low scores
        if score.score < 70:
            score.recommendations.extend([
                "Review naming conventions across all endpoints and schemas",
                "Standardize response formats and error structures",
                "Ensure consistent HTTP method usage patterns"
            ])
        elif score.score < 85:
            score.recommendations.extend([
                "Minor consistency improvements needed in naming or response formats",
                "Consider creating API design guidelines document"
            ])
        
        self.scorecard.category_scores[category] = score
