# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin3:
    def _check_url_structure_consistency(self) -> float:
        """Check URL structure and pattern consistency."""
        paths = self.spec.get('paths', {})
        
        total_paths = len(paths)
        if total_paths == 0:
            return 0
        
        structure_score = 0
        
        # Check for consistent versioning
        versioned_paths = 0
        for path in paths.keys():
            if re.search(r'/v\d+/', path):
                versioned_paths += 1
        
        # Either all or none should be versioned for consistency
        if versioned_paths == 0 or versioned_paths == total_paths:
            structure_score += 25
        elif versioned_paths > total_paths * 0.8:
            structure_score += 20
        
        # Check for reasonable path depth
        reasonable_depth = 0
        for path in paths.keys():
            segments = [seg for seg in path.split('/') if seg]
            if 2 <= len(segments) <= 5:  # Reasonable depth
                reasonable_depth += 1
        
        structure_score += (reasonable_depth / total_paths) * 25
        
        # Check for RESTful resource patterns
        restful_patterns = 0
        for path in paths.keys():
            # Look for patterns like /resources/{id} or /resources
            if re.match(r'^/[a-z-]+(/\{[^}]+\})?(/[a-z-]+)*$', path):
                restful_patterns += 1
        
        structure_score += (restful_patterns / total_paths) * 30
        
        # Check for consistent trailing slash usage
        with_slash = sum(1 for path in paths.keys() if path.endswith('/'))
        without_slash = total_paths - with_slash
        
        # Either all or none should have trailing slashes
        if with_slash == 0 or without_slash == 0:
            structure_score += 20
        elif min(with_slash, without_slash) < total_paths * 0.1:
            structure_score += 15
        
        return min(structure_score, 100)
    def _check_http_method_consistency(self) -> float:
        """Check HTTP method usage consistency."""
        paths = self.spec.get('paths', {})
        
        method_usage = {}
        total_operations = 0
        
        for path, path_obj in paths.items():
            if not isinstance(path_obj, dict):
                continue
                
            for method in path_obj.keys():
                if method.upper() in self.http_methods:
                    method_upper = method.upper()
                    total_operations += 1
                    
                    # Analyze method usage patterns
                    if method_upper not in method_usage:
                        method_usage[method_upper] = {'count': 0, 'appropriate': 0}
                    
                    method_usage[method_upper]['count'] += 1
                    
                    # Check if method usage seems appropriate
                    if self._is_method_usage_appropriate(path, method_upper, path_obj[method]):
                        method_usage[method_upper]['appropriate'] += 1
        
        if total_operations == 0:
            return 0
        
        # Calculate appropriateness score
        total_appropriate = sum(data['appropriate'] for data in method_usage.values())
        return (total_appropriate / total_operations) * 100
    def _is_method_usage_appropriate(self, path: str, method: str, operation: Dict) -> bool:
        """Check if HTTP method usage is appropriate for the endpoint."""
        # Simple heuristics for method appropriateness
        has_request_body = 'requestBody' in operation
        path_has_id = '{' in path and '}' in path
        
        if method == 'GET':
            return not has_request_body  # GET should not have body
        elif method == 'POST':
            return not path_has_id  # POST typically for collections
        elif method == 'PUT':
            return path_has_id and has_request_body  # PUT for specific resources
        elif method == 'PATCH':
            return path_has_id  # PATCH for specific resources
        elif method == 'DELETE':
            return path_has_id  # DELETE for specific resources
        
        return True  # Default to appropriate for other methods
