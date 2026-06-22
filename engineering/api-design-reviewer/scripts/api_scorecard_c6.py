# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin6:
    def _check_parameter_documentation(self) -> float:
        """Check parameter documentation completeness."""
        paths = self.spec.get('paths', {})
        
        total_params = 0
        documented_params = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                parameters = operation.get('parameters', [])
                for param in parameters:
                    if not isinstance(param, dict):
                        continue
                    
                    total_params += 1
                    
                    doc_score = 0
                    if param.get('description'):
                        doc_score += 1
                    if param.get('example') or (param.get('schema', {}).get('example')):
                        doc_score += 1
                    
                    if doc_score >= 1:  # At least description
                        documented_params += 1
        
        return (documented_params / total_params * 100) if total_params > 0 else 100
    def _check_response_documentation(self) -> float:
        """Check response documentation completeness."""
        paths = self.spec.get('paths', {})
        
        total_responses = 0
        documented_responses = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                responses = operation.get('responses', {})
                for status_code, response in responses.items():
                    if not isinstance(response, dict):
                        continue
                    
                    total_responses += 1
                    
                    if response.get('description'):
                        documented_responses += 1
        
        return (documented_responses / total_responses * 100) if total_responses > 0 else 100
    def _check_example_coverage(self) -> float:
        """Check example coverage across the API."""
        paths = self.spec.get('paths', {})
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        # Check examples in operations
        total_operations = 0
        operations_with_examples = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                total_operations += 1
                
                has_example = False
                
                # Check request body examples
                request_body = operation.get('requestBody', {})
                if self._has_examples(request_body.get('content', {})):
                    has_example = True
                
                # Check response examples
                responses = operation.get('responses', {})
                for response in responses.values():
                    if isinstance(response, dict) and self._has_examples(response.get('content', {})):
                        has_example = True
                        break
                
                if has_example:
                    operations_with_examples += 1
        
        # Check examples in schemas
        total_schemas = len(schemas)
        schemas_with_examples = 0
        
        for schema in schemas.values():
            if isinstance(schema, dict) and self._schema_has_examples(schema):
                schemas_with_examples += 1
        
        # Combine scores
        operation_score = (operations_with_examples / total_operations * 100) if total_operations > 0 else 100
        schema_score = (schemas_with_examples / total_schemas * 100) if total_schemas > 0 else 100
        
        return (operation_score + schema_score) / 2
