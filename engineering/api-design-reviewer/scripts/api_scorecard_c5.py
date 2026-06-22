# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin5:
    def _check_api_level_documentation(self) -> float:
        """Check API-level documentation completeness."""
        info = self.spec.get('info', {})
        score = 0
        
        # Required fields
        if info.get('title'):
            score += 20
        if info.get('version'):
            score += 20
        if info.get('description') and len(info['description']) > 20:
            score += 30
        
        # Optional but recommended fields
        if info.get('contact'):
            score += 15
        if info.get('license'):
            score += 15
        
        return score
    def _check_endpoint_documentation(self) -> float:
        """Check endpoint-level documentation completeness."""
        paths = self.spec.get('paths', {})
        
        total_operations = 0
        documented_operations = 0
        
        for path_obj in paths.values():
            if not isinstance(path_obj, dict):
                continue
                
            for method, operation in path_obj.items():
                if method.upper() not in self.http_methods:
                    continue
                
                total_operations += 1
                doc_score = 0
                
                if operation.get('summary'):
                    doc_score += 1
                if operation.get('description') and len(operation['description']) > 20:
                    doc_score += 1
                if operation.get('operationId'):
                    doc_score += 1
                
                # Consider it documented if it has at least 2/3 elements
                if doc_score >= 2:
                    documented_operations += 1
        
        return (documented_operations / total_operations * 100) if total_operations > 0 else 100
    def _check_schema_documentation(self) -> float:
        """Check schema documentation completeness."""
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        if not schemas:
            return 80  # No schemas to document
        
        total_schemas = len(schemas)
        documented_schemas = 0
        
        for schema_name, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            
            doc_elements = 0
            
            # Schema-level description
            if schema.get('description'):
                doc_elements += 1
            
            # Property descriptions
            properties = schema.get('properties', {})
            if properties:
                described_props = sum(1 for prop in properties.values() 
                                    if isinstance(prop, dict) and prop.get('description'))
                if described_props > len(properties) * 0.5:  # At least 50% documented
                    doc_elements += 1
            
            # Examples
            if schema.get('example') or any(
                isinstance(prop, dict) and prop.get('example') 
                for prop in properties.values()
            ):
                doc_elements += 1
            
            if doc_elements >= 2:
                documented_schemas += 1
        
        return (documented_schemas / total_schemas * 100) if total_schemas > 0 else 100
