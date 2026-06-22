# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin10:
    def _check_error_handling(self) -> float:
        """Check error handling quality."""
        paths = self.spec.get('paths', {})
        
        total_operations = 0
        operations_with_errors = 0
        detailed_error_responses = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                total_operations += 1
                responses = operation.get('responses', {})
                
                # Check for error responses
                has_error_responses = any(
                    status_code.startswith('4') or status_code.startswith('5')
                    for status_code in responses.keys()
                )
                
                if has_error_responses:
                    operations_with_errors += 1
                    
                    # Check for detailed error schemas
                    for status_code, response in responses.items():
                        if (status_code.startswith('4') or status_code.startswith('5')) and isinstance(response, dict):
                            content = response.get('content', {})
                            for media_obj in content.values():
                                schema = media_obj.get('schema', {})
                                if self._has_detailed_error_schema(schema):
                                    detailed_error_responses += 1
                                    break
                            break
        
        if total_operations == 0:
            return 0
        
        error_coverage = (operations_with_errors / total_operations) * 60
        error_detail = (detailed_error_responses / operations_with_errors * 40) if operations_with_errors > 0 else 0
        
        return error_coverage + error_detail
    def _has_detailed_error_schema(self, schema: Dict[str, Any]) -> bool:
        """Check if error schema has detailed information."""
        if not isinstance(schema, dict):
            return False
        
        properties = schema.get('properties', {})
        error_fields = {'error', 'message', 'details', 'code', 'timestamp'}
        
        matching_fields = sum(1 for field in error_fields if field in properties)
        return matching_fields >= 2  # At least 2 standard error fields
    def _check_filtering_and_searching(self) -> float:
        """Check filtering and search capabilities."""
        paths = self.spec.get('paths', {})
        
        collection_endpoints = 0
        endpoints_with_filtering = 0
        
        for path, path_obj in paths.items():
            if not isinstance(path_obj, dict):
                continue
            
            # Identify collection endpoints (no path parameters)
            if '{' not in path:
                get_operation = path_obj.get('get')
                if get_operation:
                    collection_endpoints += 1
                    
                    # Check for filtering/search parameters
                    parameters = get_operation.get('parameters', [])
                    filter_params = {'filter', 'search', 'q', 'query', 'limit', 'page', 'offset'}
                    
                    has_filtering = any(
                        isinstance(param, dict) and param.get('name', '').lower() in filter_params
                        for param in parameters
                    )
                    
                    if has_filtering:
                        endpoints_with_filtering += 1
        
        return (endpoints_with_filtering / collection_endpoints * 100) if collection_endpoints > 0 else 100
