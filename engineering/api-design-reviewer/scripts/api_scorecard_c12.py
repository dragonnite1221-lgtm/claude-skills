# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402
from api_scorecard_p0 import CategoryScore, ScoreCategory  # noqa: F401,E501


class APIScoringEngineMixin12:
    def _score_performance(self) -> None:
        """Score API performance patterns (15% weight)."""
        category = ScoreCategory.PERFORMANCE
        score = CategoryScore(
            category=category,
            score=0.0,
            max_score=100.0,
            weight=self.category_weights[category]
        )
        
        performance_checks = [
            self._check_caching_headers(),
            self._check_pagination_patterns(),
            self._check_compression_support(),
            self._check_efficiency_patterns(),
            self._check_batch_operations()
        ]
        
        valid_scores = [s for s in performance_checks if s is not None]
        if valid_scores:
            score.score = sum(valid_scores) / len(valid_scores)
        
        # Add recommendations
        if score.score < 60:
            score.recommendations.extend([
                "Implement pagination for list endpoints",
                "Add caching headers for cacheable responses",
                "Consider batch operations for bulk updates"
            ])
        elif score.score < 80:
            score.recommendations.extend([
                "Review caching strategies for better performance",
                "Consider field selection parameters for large responses"
            ])
        
        self.scorecard.category_scores[category] = score
    def _check_caching_headers(self) -> float:
        """Check caching header implementation."""
        paths = self.spec.get('paths', {})
        
        get_operations = 0
        cacheable_operations = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
            
            get_operation = path_obj.get('get')
            if get_operation and isinstance(get_operation, dict):
                get_operations += 1
                
                # Check for caching-related headers in responses
                responses = get_operation.get('responses', {})
                for response in responses.values():
                    if not isinstance(response, dict):
                        continue
                    
                    headers = response.get('headers', {})
                    cache_headers = {'cache-control', 'etag', 'last-modified', 'expires'}
                    
                    if any(header.lower() in cache_headers for header in headers.keys()):
                        cacheable_operations += 1
                        break
        
        return (cacheable_operations / get_operations * 100) if get_operations > 0 else 50
    def _check_pagination_patterns(self) -> float:
        """Check pagination implementation."""
        paths = self.spec.get('paths', {})
        
        collection_endpoints = 0
        paginated_endpoints = 0
        
        for path, path_obj in paths.items():
            if not isinstance(path_obj, dict):
                continue
            
            # Identify collection endpoints
            if '{' not in path:  # No path parameters = collection
                get_operation = path_obj.get('get')
                if get_operation and isinstance(get_operation, dict):
                    collection_endpoints += 1
                    
                    # Check for pagination parameters
                    parameters = get_operation.get('parameters', [])
                    pagination_params = {'limit', 'offset', 'page', 'pagesize', 'per_page', 'cursor'}
                    
                    has_pagination = any(
                        isinstance(param, dict) and param.get('name', '').lower() in pagination_params
                        for param in parameters
                    )
                    
                    if has_pagination:
                        paginated_endpoints += 1
        
        return (paginated_endpoints / collection_endpoints * 100) if collection_endpoints > 0 else 100
