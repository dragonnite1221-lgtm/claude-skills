# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin2:
    def _check_error_format_consistency(self) -> float:
        """Check error response format consistency."""
        paths = self.spec.get('paths', {})
        error_responses = []
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                responses = operation.get('responses', {})
                for status_code, response in responses.items():
                    try:
                        code_int = int(status_code)
                        if code_int >= 400:  # Error responses
                            content = response.get('content', {})
                            for media_type, media_obj in content.items():
                                schema = media_obj.get('schema', {})
                                error_responses.append(self._extract_schema_pattern(schema))
                    except ValueError:
                        continue
        
        if not error_responses:
            return 80  # No error responses defined - somewhat concerning
        
        # Check consistency of error response formats
        pattern_counts = {}
        for pattern in error_responses:
            pattern_key = json.dumps(pattern, sort_keys=True)
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
        
        max_count = max(pattern_counts.values()) if pattern_counts else 0
        consistency_ratio = max_count / len(error_responses) if error_responses else 1
        
        return consistency_ratio * 100
    def _check_parameter_consistency(self) -> float:
        """Check parameter naming and usage consistency."""
        paths = self.spec.get('paths', {})
        
        query_params = []
        path_params = []
        header_params = []
        
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
                        
                    param_name = param.get('name', '')
                    param_in = param.get('in', '')
                    
                    if param_in == 'query':
                        query_params.append(param_name)
                    elif param_in == 'path':
                        path_params.append(param_name)
                    elif param_in == 'header':
                        header_params.append(param_name)
        
        # Check naming consistency for each parameter type
        scores = []
        
        # Query parameters should be camelCase or kebab-case
        if query_params:
            valid_query = sum(1 for p in query_params 
                            if self.camel_case_pattern.match(p) or self.kebab_case_pattern.match(p))
            scores.append((valid_query / len(query_params)) * 100)
        
        # Path parameters should be camelCase or kebab-case
        if path_params:
            valid_path = sum(1 for p in path_params 
                           if self.camel_case_pattern.match(p) or self.kebab_case_pattern.match(p))
            scores.append((valid_path / len(path_params)) * 100)
        
        return sum(scores) / len(scores) if scores else 100
