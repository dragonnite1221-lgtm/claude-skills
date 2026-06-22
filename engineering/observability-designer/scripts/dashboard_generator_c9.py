# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dashboard_generator_base import *  # noqa: F403,E402


class DashboardGeneratorMixin9:
    def generate_documentation(self, dashboard_spec: Dict[str, Any]) -> str:
        """Generate documentation for the dashboard."""
        metadata = dashboard_spec['metadata']
        service = metadata['service']
        
        doc_content = f"""# {metadata['title']} Documentation

## Overview
This dashboard provides comprehensive monitoring for {service['name']}, a {service['type']} service with {service['criticality']} criticality.

**Target Audience:** {metadata['target_role'].upper()} teams
**Generated:** {metadata['generated_at']}

## Dashboard Sections

### Service Overview
- **Service Status**: Real-time availability status
- **SLO Achievement**: 30-day SLO compliance metrics
- **Error Budget**: Remaining error budget visualization

### Golden Signals Monitoring
- **Latency**: P50, P95, P99 response times
- **Traffic**: Request rate by status code
- **Errors**: Error rates for 4xx and 5xx responses
- **Saturation**: CPU and memory utilization

### Resource Utilization
- **CPU Usage**: Process CPU consumption
- **Memory Usage**: Memory utilization tracking
- **Network I/O**: Network throughput metrics
- **Disk I/O**: Disk read/write operations

## Key Metrics

### SLIs Tracked
"""
        
        # Add service-type specific metrics
        service_type = service.get('type', 'api')
        if service_type in self.SERVICE_METRICS:
            metrics = self.SERVICE_METRICS[service_type]['key_metrics']
            for metric in metrics:
                doc_content += f"- `{metric}`: Core service metric\n"
        
        doc_content += f"""
## Alert Integration
- Active alerts are displayed in context with relevant panels
- Alert annotations show on time series charts
- Click-through to alert management system available

## Drill-Down Paths
"""
        
        drill_downs = dashboard_spec.get('drill_down_paths', {})
        for path_name, path_config in drill_downs.items():
            doc_content += f"- **{path_name}**: From {path_config['from']} → {path_config['to']}\n"
        
        doc_content += f"""
## Usage Guidelines

### Time Ranges
Use appropriate time ranges for different investigation types:
- **Real-time monitoring**: 15m - 1h
- **Recent incident investigation**: 1h - 6h  
- **Trend analysis**: 1d - 7d
- **Capacity planning**: 7d - 30d

### Variables
- **environment**: Filter by deployment environment
- **instance**: Focus on specific service instances
- **handler**: Filter by API endpoint or handler

### Performance Optimization
- Use longer time ranges for capacity planning
- Refresh intervals are optimized per role:
  - SRE: 30s for operational awareness
  - Developer: 1m for troubleshooting
  - Executive: 5m for high-level monitoring

## Maintenance
- Dashboard panels automatically adapt to service changes
- Template variables refresh based on actual metric labels
- Review and update business metrics quarterly
"""
        
        return doc_content
    def export_specification(self, dashboard_spec: Dict[str, Any], output_file: str, 
                           format_type: str = 'json'):
        """Export dashboard specification."""
        if format_type.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(dashboard_spec, f, indent=2)
        elif format_type.lower() == 'grafana':
            grafana_json = self.generate_grafana_json(dashboard_spec)
            with open(output_file, 'w') as f:
                json.dump(grafana_json, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
