# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scorecard_base import *  # noqa: F403,E402


class APIScoringEngineMixin8:
    def _check_https_usage(self) -> float:
        """Check HTTPS enforcement."""
        servers = self.spec.get('servers', [])
        
        if not servers:
            return 60  # No servers defined - assume HTTPS
        
        https_servers = 0
        for server in servers:
            if isinstance(server, dict):
                url = server.get('url', '')
                if url.startswith('https://') or not url.startswith('http://'):
                    https_servers += 1
        
        return (https_servers / len(servers) * 100) if servers else 100
    def _check_authentication_patterns(self) -> float:
        """Check authentication pattern quality."""
        security_schemes = self.spec.get('components', {}).get('securitySchemes', {})
        
        if not security_schemes:
            return 0
        
        pattern_scores = []
        
        for scheme in security_schemes.values():
            if not isinstance(scheme, dict):
                continue
            
            scheme_type = scheme.get('type', '').lower()
            
            if scheme_type == 'oauth2':
                # OAuth2 is highly recommended
                flows = scheme.get('flows', {})
                if flows:
                    pattern_scores.append(95)
                else:
                    pattern_scores.append(80)
            elif scheme_type == 'http':
                scheme_scheme = scheme.get('scheme', '').lower()
                if scheme_scheme == 'bearer':
                    pattern_scores.append(85)
                elif scheme_scheme == 'basic':
                    pattern_scores.append(60)  # Less secure
                else:
                    pattern_scores.append(70)
            elif scheme_type == 'apikey':
                location = scheme.get('in', '').lower()
                if location == 'header':
                    pattern_scores.append(75)
                else:
                    pattern_scores.append(60)  # Query/cookie less secure
            else:
                pattern_scores.append(50)  # Unknown scheme
        
        return sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0
    def _check_sensitive_data_handling(self) -> float:
        """Check sensitive data handling patterns."""
        # This is a simplified check - in reality would need more sophisticated analysis
        schemas = self.spec.get('components', {}).get('schemas', {})
        
        score = 80  # Default good score
        
        # Look for potential sensitive fields without proper handling
        sensitive_field_names = {'password', 'secret', 'token', 'key', 'ssn', 'credit_card'}
        
        for schema in schemas.values():
            if not isinstance(schema, dict):
                continue
            
            properties = schema.get('properties', {})
            for prop_name, prop_def in properties.items():
                if not isinstance(prop_def, dict):
                    continue
                
                # Check for sensitive field names
                if any(sensitive in prop_name.lower() for sensitive in sensitive_field_names):
                    # Check if it's marked as sensitive (writeOnly, format: password, etc.)
                    if not (prop_def.get('writeOnly') or 
                           prop_def.get('format') == 'password' or
                           'password' in prop_def.get('description', '').lower()):
                        score -= 10  # Penalty for exposed sensitive field
        
        return max(score, 0)
