# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin1:
    def _generate_panels(self, service_def: Dict[str, Any], 
                        role_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dashboard panels based on service and role."""
        service_name = service_def.get('name', 'service')
        service_type = service_def.get('type', 'api')
        panels = []
        
        # Service Overview Panels
        panels.extend(self._create_overview_panels(service_def))
        
        # Golden Signals Panels
        panels.extend(self._create_golden_signals_panels(service_def))
        
        # Resource Utilization Panels
        panels.extend(self._create_resource_panels(service_def))
        
        # Service-specific panels
        if service_type == 'api':
            panels.extend(self._create_api_specific_panels(service_def))
        elif service_type == 'database':
            panels.extend(self._create_database_specific_panels(service_def))
        elif service_type == 'queue':
            panels.extend(self._create_queue_specific_panels(service_def))
        
        # Role-specific additional panels
        if 'business_metrics' in role_config['primary_focus']:
            panels.extend(self._create_business_metrics_panels(service_def))
        
        if 'capacity' in role_config['primary_focus']:
            panels.extend(self._create_capacity_panels(service_def))
        
        return panels
