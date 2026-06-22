# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin1:
    def _check_naming_consistency(self) -> float:
        """Check naming convention consistency."""
        paths = self.spec.get('paths', {})
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        total_checks = 0
        passed_checks = 0
        
        # Check path naming (should be kebab-case)
        for path in paths.keys():
            segments = [seg for seg in path.split('/') if seg and not seg.startswith('{')]
            for segment in segments:
                total_checks += 1
                if self.kebab_case_pattern.match(segment) or re.match(r'^v\d+$', segment):
                    passed_checks += 1
        
        # Check schema naming (should be PascalCase)
        for schema_name in schemas.keys():
            total_checks += 1
            if self.pascal_case_pattern.match(schema_name):
                passed_checks += 1
        
        # Check property naming within schemas
        for schema in schemas.values():
            if isinstance(schema, dict) and 'properties' in schema:
                for prop_name in schema['properties'].keys():
                    total_checks += 1
                    if self.camel_case_pattern.match(prop_name):
                        passed_checks += 1
        
        return (passed_checks / total_checks * 100) if total_checks > 0 else 100
    def _check_response_consistency(self) -> float:
        """Check response format consistency."""
        paths = self.spec.get('paths', {})
        
        response_patterns = []
        total_responses = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods or not isinstance(operation, dict):
                    continue
                
                responses = operation.get('responses', {})
                for status_code, response in responses.items():
                    if not isinstance(response, dict):
                        continue
                        
                    total_responses += 1
                    content = response.get('content', {})
                    
                    # Analyze response structure
                    for media_type, media_obj in content.items():
                        schema = media_obj.get('schema', {})
                        pattern = self._extract_schema_pattern(schema)
                        response_patterns.append(pattern)
        
        # Calculate consistency by comparing patterns
        if not response_patterns:
            return 100
        
        pattern_counts = {}
        for pattern in response_patterns:
            pattern_key = json.dumps(pattern, sort_keys=True)
            pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1
        
        # Most common pattern should dominate for good consistency
        max_count = max(pattern_counts.values()) if pattern_counts else 0
        consistency_ratio = max_count / len(response_patterns) if response_patterns else 1
        
        return consistency_ratio * 100
    def _extract_schema_pattern(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a pattern from a schema for consistency checking."""
        if not isinstance(schema, dict):
            return {}
        
        pattern = {
            'type': schema.get('type'),
            'has_properties': 'properties' in schema,
            'has_items': 'items' in schema,
            'required_count': len(schema.get('required', [])),
            'property_count': len(schema.get('properties', {}))
        }
        
        return pattern
