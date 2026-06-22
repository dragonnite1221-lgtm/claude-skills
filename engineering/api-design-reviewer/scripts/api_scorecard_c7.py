# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402
from api_scorecard_p0 import CategoryScore, ScoreCategory  # noqa: F401,E501


class APIScoringEngineMixin7:
    def _has_examples(self, content: Dict[str, Any]) -> bool:
        """Check if content has examples."""
        for media_type, media_obj in content.items():
            if isinstance(media_obj, dict):
                if media_obj.get('example') or media_obj.get('examples'):
                    return True
        return False
    def _schema_has_examples(self, schema: Dict[str, Any]) -> bool:
        """Check if schema has examples."""
        if schema.get('example'):
            return True
        
        properties = schema.get('properties', {})
        for prop in properties.values():
            if isinstance(prop, dict) and prop.get('example'):
                return True
        
        return False
    def _score_security(self) -> None:
        """Score API security implementation (20% weight)."""
        category = ScoreCategory.SECURITY
        score = CategoryScore(
            category=category,
            score=0.0,
            max_score=100.0,
            weight=self.category_weights[category]
        )
        
        security_checks = [
            self._check_security_schemes(),
            self._check_security_requirements(),
            self._check_https_usage(),
            self._check_authentication_patterns(),
            self._check_sensitive_data_handling()
        ]
        
        valid_scores = [s for s in security_checks if s is not None]
        if valid_scores:
            score.score = sum(valid_scores) / len(valid_scores)
        
        # Add recommendations
        if score.score < 50:
            score.recommendations.extend([
                "Implement comprehensive security schemes (OAuth2, API keys, etc.)",
                "Ensure all endpoints have appropriate security requirements",
                "Add input validation and rate limiting patterns"
            ])
        elif score.score < 80:
            score.recommendations.extend([
                "Review security coverage for all endpoints",
                "Consider additional security measures for sensitive operations"
            ])
        
        self.scorecard.category_scores[category] = score
    def _check_security_schemes(self) -> float:
        """Check security scheme definitions."""
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        
        if not security_schemes:
            return 20  # Very low score for no security
        
        score = 40  # Base score for having security schemes
        
        scheme_types = set()
        for scheme in security_schemes.values():
            if isinstance(scheme, dict):
                scheme_type = scheme.get('type')
                scheme_types.add(scheme_type)
        
        # Bonus for modern security schemes
        if 'oauth2' in scheme_types:
            score += 30
        if 'apiKey' in scheme_types:
            score += 15
        if 'http' in scheme_types:
            score += 15
        
        return min(score, 100)
    def _check_security_requirements(self) -> float:
        """Check security requirement coverage."""
        paths = self.spec.get('paths', {})
        global_security = self.spec.get('security', [])
        
        total_operations = 0
        secured_operations = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                total_operations += 1
                
                # Check if operation has security requirements
                operation_security = operation.get('security')
                
                if operation_security is not None:
                    secured_operations += 1
                elif global_security:
                    secured_operations += 1
        
        return (secured_operations / total_operations * 100) if total_operations > 0 else 0
