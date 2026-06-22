# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin11:
    def _check_resource_relationships(self) -> float:
        """Check resource relationship handling."""
        paths = self.spec.get('paths', {})
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        # Look for nested resource patterns
        nested_resources = 0
        total_resource_paths = 0
        
        for path in paths.keys():
            # Skip root paths
            if path.count('/') >= 3:  # e.g., /api/users/123/orders
                total_resource_paths += 1
                if '{' in path:
                    nested_resources += 1
        
        # Look for relationship fields in schemas
        schemas_with_relations = 0
        for schema in schemas.values():
            if not isinstance(schema, dict):
                continue
            
            properties = schema.get('properties', {})
            relation_indicators = {'id', '_id', 'ref', 'link', 'relationship'}
            
            has_relations = any(
                any(indicator in prop_name.lower() for indicator in relation_indicators)
                for prop_name in properties.keys()
            )
            
            if has_relations:
                schemas_with_relations += 1
        
        nested_score = (nested_resources / total_resource_paths * 50) if total_resource_paths > 0 else 25
        schema_score = (schemas_with_relations / len(schemas) * 50) if schemas else 25
        
        return nested_score + schema_score
    def _check_developer_experience(self) -> float:
        """Check overall developer experience factors."""
        # This is a composite score based on various DX factors
        factors = []
        
        # Factor 1: Consistent response structure
        factors.append(self._check_response_consistency())
        
        # Factor 2: Clear operation IDs
        paths = self.spec.get('paths', {})
        total_operations = 0
        operations_with_ids = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                total_operations += 1
                if isinstance(operation, dict) and operation.get('operationId'):
                    operations_with_ids += 1
        
        operation_id_score = (operations_with_ids / total_operations * 100) if total_operations > 0 else 100
        factors.append(operation_id_score)
        
        # Factor 3: Reasonable path complexity
        avg_path_complexity = 0
        if paths:
            complexities = []
            for path in paths.keys():
                segments = [seg for seg in path.split('/') if seg]
                complexities.append(len(segments))
            
            avg_complexity = sum(complexities) / len(complexities)
            # Optimal complexity is 3-4 segments
            if 3 <= avg_complexity <= 4:
                avg_path_complexity = 100
            elif 2 <= avg_complexity <= 5:
                avg_path_complexity = 80
            else:
                avg_path_complexity = 60
        
        factors.append(avg_path_complexity)
        
        return sum(factors) / len(factors) if factors else 0
