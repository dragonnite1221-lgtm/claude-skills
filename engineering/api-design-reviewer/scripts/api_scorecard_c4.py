# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402
from api_scorecard_p0 import CategoryScore, ScoreCategory  # noqa: F401,E501


class APIScoringEngineMixin4:
    def _check_status_code_consistency(self) -> float:
        """Check HTTP status code usage consistency."""
        paths = self.spec.get('paths', {})
        
        method_status_patterns = {}
        total_operations = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                total_operations += 1
                responses = operation.get('responses', {})
                status_codes = set(responses.keys())
                
                if method.upper() not in method_status_patterns:
                    method_status_patterns[method.upper()] = []
                
                method_status_patterns[method.upper()].append(status_codes)
        
        if total_operations == 0:
            return 0
        
        # Check consistency within each method type
        consistency_scores = []
        
        for method, status_patterns in method_status_patterns.items():
            if not status_patterns:
                continue
            
            # Find common status codes for this method
            all_codes = set()
            for pattern in status_patterns:
                all_codes.update(pattern)
            
            # Calculate how many operations use the most common codes
            code_usage = {}
            for code in all_codes:
                code_usage[code] = sum(1 for pattern in status_patterns if code in pattern)
            
            # Score based on consistency of common status codes
            if status_patterns:
                avg_consistency = sum(
                    len([code for code in pattern if code_usage.get(code, 0) > len(status_patterns) * 0.5]) 
                    for pattern in status_patterns
                ) / len(status_patterns)
                
                method_consistency = min(avg_consistency / 3.0 * 100, 100)  # Expect ~3 common codes
                consistency_scores.append(method_consistency)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 100
    def _score_documentation(self) -> None:
        """Score API documentation quality (20% weight)."""
        category = ScoreCategory.DOCUMENTATION
        score = CategoryScore(
            category=category,
            score=0.0,
            max_score=100.0,
            weight=self.category_weights[category]
        )
        
        documentation_checks = [
            self._check_api_level_documentation(),
            self._check_endpoint_documentation(),
            self._check_schema_documentation(),
            self._check_parameter_documentation(),
            self._check_response_documentation(),
            self._check_example_coverage()
        ]
        
        valid_scores = [s for s in documentation_checks if s is not None]
        if valid_scores:
            score.score = sum(valid_scores) / len(valid_scores)
        
        # Add recommendations based on score
        if score.score < 60:
            score.recommendations.extend([
                "Add comprehensive descriptions to all API components",
                "Include examples for complex operations and schemas",
                "Document all parameters and response fields"
            ])
        elif score.score < 80:
            score.recommendations.extend([
                "Improve documentation completeness for some endpoints",
                "Add more examples to enhance developer experience"
            ])
        
        self.scorecard.category_scores[category] = score
