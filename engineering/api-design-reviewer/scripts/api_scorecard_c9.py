# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402
from api_scorecard_p0 import CategoryScore, ScoreCategory  # noqa: F401,E501


class APIScoringEngineMixin9:
    def _score_usability(self) -> None:
        """Score API usability and developer experience (15% weight)."""
        category = ScoreCategory.USABILITY
        score = CategoryScore(
            category=category,
            score=0.0,
            max_score=100.0,
            weight=self.category_weights[category]
        )
        
        usability_checks = [
            self._check_discoverability(),
            self._check_error_handling(),
            self._check_filtering_and_searching(),
            self._check_resource_relationships(),
            self._check_developer_experience()
        ]
        
        valid_scores = [s for s in usability_checks if s is not None]
        if valid_scores:
            score.score = sum(valid_scores) / len(valid_scores)
        
        # Add recommendations
        if score.score < 60:
            score.recommendations.extend([
                "Improve error messages with actionable guidance",
                "Add filtering and search capabilities to list endpoints",
                "Enhance resource discoverability with better linking"
            ])
        elif score.score < 80:
            score.recommendations.extend([
                "Consider adding HATEOAS links for better discoverability",
                "Enhance developer experience with better examples"
            ])
        
        self.scorecard.category_scores[category] = score
    def _check_discoverability(self) -> float:
        """Check API discoverability features."""
        paths = self.spec.get('paths', {})
        
        # Look for root/discovery endpoints
        has_root = '/' in paths or any(path == '/api' or path.startswith('/api/') for path in paths)
        
        # Look for HATEOAS patterns in responses
        hateoas_score = 0
        total_responses = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                responses = operation.get('responses', {})
                for response in responses.values():
                    if not isinstance(response, dict):
                        continue
                    
                    total_responses += 1
                    
                    # Look for link-like properties in response schemas
                    content = response.get('content', {})
                    for media_obj in content.values():
                        schema = media_obj.get('schema', {})
                        if self._has_link_properties(schema):
                            hateoas_score += 1
                            break
        
        discovery_score = 50 if has_root else 30
        if total_responses > 0:
            hateoas_ratio = hateoas_score / total_responses
            discovery_score += hateoas_ratio * 50
        
        return min(discovery_score, 100)
    def _has_link_properties(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has link-like properties."""
        if not isinstance(schema, dict):
            return False
        
        properties = schema.get('properties', {})
        link_indicators = {'links', '_links', 'href', 'url', 'self', 'next', 'prev'}
        
        return any(prop_name.lower() in link_indicators for prop_name in properties.keys())
