# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402


class SLODesignerMixin5:
    def print_summary(self, framework: Dict[str, Any]):
        """Print human-readable summary of the SLO framework."""
        service = framework['metadata']['service']
        slis = framework['slis']
        slos = framework['slos']
        error_budgets = framework['error_budgets']
        
        print(f"\n{'='*60}")
        print(f"SLO FRAMEWORK SUMMARY FOR {service['name'].upper()}")
        print(f"{'='*60}")
        
        print(f"\nService Details:")
        print(f"  Type: {service['type']}")
        print(f"  Criticality: {service['criticality']}")
        print(f"  User Facing: {'Yes' if service.get('user_facing') else 'No'}")
        print(f"  Team: {service.get('team', 'Unknown')}")
        
        print(f"\nService Level Indicators ({len(slis)}):")
        for i, sli in enumerate(slis, 1):
            print(f"  {i}. {sli['name']}")
            print(f"     Description: {sli['description']}")
            print(f"     Type: {sli['type']}")
            print()
        
        print(f"Service Level Objectives ({len(slos)}):")
        for i, slo in enumerate(slos, 1):
            print(f"  {i}. {slo['name']}")
            print(f"     Target: {slo['target_display']}")
            print(f"     Measurement Window: {slo['measurement_window']}")
            print()
        
        print(f"Error Budget Summary:")
        for budget in error_budgets:
            print(f"  {budget['slo_name']}:")
            print(f"    Monthly Budget: {budget['error_budget_percentage']}")
            print(f"    Burn Rate Alerts: {len(budget['burn_rate_alerts'])}")
            print()
        
        sla = framework['sla_recommendations']
        if sla['applicable']:
            print(f"SLA Recommendations:")
            print(f"  Commitments: {len(sla['commitments'])}")
            print(f"  Penalty Tiers: {len(sla['penalties'])}")
        else:
            print(f"SLA Recommendations: {sla['reason']}")
        
        print(f"\nImplementation Timeline: 1-2 weeks")
        print(f"Framework generated at: {framework['metadata']['generated_at']}")
        print(f"{'='*60}\n")
