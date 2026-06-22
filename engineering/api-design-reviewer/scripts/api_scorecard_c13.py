# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin13:
    def _check_compression_support(self) -> float:
        """Check compression support indicators."""
        # This is speculative - OpenAPI doesn't directly specify compression
        # Look for indicators that compression is considered
        
        servers = self.spec.get('servers', [])
        
        # Check if any server descriptions mention compression
        compression_mentions = 0
        for server in servers:
            if isinstance(server, dict):
                description = server.get('description', '').lower()
                if any(term in description for term in ['gzip', 'compress', 'deflate']):
                    compression_mentions += 1
        
        # Base score - assume compression is handled at server level
        base_score = 70
        
        if compression_mentions > 0:
            return min(base_score + (compression_mentions * 10), 100)
        
        return base_score
    def _check_efficiency_patterns(self) -> float:
        """Check efficiency patterns like field selection."""
        paths = self.spec.get('paths', {})
        
        total_get_operations = 0
        operations_with_selection = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
            
            get_operation = path_obj.get('get')
            if get_operation and isinstance(get_operation, dict):
                total_get_operations += 1
                
                # Check for field selection parameters
                parameters = get_operation.get('parameters', [])
                selection_params = {'fields', 'select', 'include', 'exclude'}
                
                has_selection = any(
                    isinstance(param, dict) and param.get('name', '').lower() in selection_params
                    for param in parameters
                )
                
                if has_selection:
                    operations_with_selection += 1
        
        return (operations_with_selection / total_get_operations * 100) if total_get_operations > 0 else 60
    def _check_batch_operations(self) -> float:
        """Check for batch operation support."""
        paths = self.spec.get('paths', {})
        
        # Look for batch endpoints
        batch_indicators = ['batch', 'bulk', 'multi']
        batch_endpoints = 0
        
        for path in paths.keys():
            if any(indicator in path.lower() for indicator in batch_indicators):
                batch_endpoints += 1
        
        # Look for array-based request bodies (indicating batch operations)
        array_operations = 0
        total_post_put_operations = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
            
            for method in ['post', 'put', 'patch']:
                operation = path_obj.get(method)
                if operation and isinstance(operation, dict):
                    total_post_put_operations += 1
                    
                    request_body = operation.get('requestBody', {})
                    content = request_body.get('content', {})
                    
                    for media_obj in content.values():
                        schema = media_obj.get('schema', {})
                        if schema.get('type') == 'array':
                            array_operations += 1
                            break
        
        # Score based on presence of batch patterns
        batch_score = min(batch_endpoints * 20, 60)  # Up to 60 points for explicit batch endpoints
        
        if total_post_put_operations > 0:
            array_score = (array_operations / total_post_put_operations) * 40
            batch_score += array_score
        
        return min(batch_score, 100)
