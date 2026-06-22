# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402


class OKRGeneratorMixin2:
    def cascade_to_teams(self, product_okrs: Dict) -> List[Dict]:
        """Cascade product OKRs to individual teams"""

        team_okrs = []
        team_contribution = 1.0 / len(self.teams) if self.teams else 0.25

        for team in self.teams:
            team_okr = {
                'level': 'Team',
                'team': team,
                'quarter': product_okrs['quarter'],
                'parent': 'Product',
                'contribution': team_contribution,
                'objectives': []
            }

            for product_obj in product_okrs['objectives']:
                if self._is_relevant_for_team(product_obj['title'], team):
                    team_obj = {
                        'id': f'{team[:3].upper()}-{product_obj["id"].split("-")[1]}',
                        'title': self._translate_to_team(product_obj['title'], team),
                        'parent_objective': product_obj['id'],
                        'key_results': [],
                        'owner': f'{team} PM',
                        'status': 'draft'
                    }

                    for kr in product_obj['key_results'][:2]:
                        team_kr = {
                            'id': f'{team[:3].upper()}-{team_obj["id"].split("-")[1]}-KR{kr["id"].split("KR")[1]}',
                            'title': self._translate_kr_to_team(kr['title'], team),
                            'contributes_to': kr['id'],
                            'current': kr['current'],
                            'target': kr['target'] * team_contribution,
                            'unit': kr['unit'],
                            'status': 'not_started'
                        }
                        team_obj['key_results'].append(team_kr)

                    team_okr['objectives'].append(team_obj)

            if team_okr['objectives']:
                team_okrs.append(team_okr)

        return team_okrs
    def generate_okr_dashboard(self, all_okrs: Dict) -> str:
        """Generate OKR dashboard view"""

        dashboard = ["=" * 60]
        dashboard.append("OKR CASCADE DASHBOARD")
        dashboard.append(f"Quarter: {all_okrs.get('quarter', 'Q1 2025')}")
        dashboard.append(f"Strategy: {all_okrs.get('strategy', 'growth').upper()}")
        dashboard.append(f"Teams: {', '.join(self.teams)}")
        dashboard.append(f"Product Contribution: {self.product_contribution * 100:.0f}%")
        dashboard.append("=" * 60)

        # Company OKRs
        if 'company' in all_okrs:
            dashboard.append("\n🏢 COMPANY OKRS\n")
            for obj in all_okrs['company']['objectives']:
                dashboard.append(f"📌 {obj['id']}: {obj['title']}")
                for kr in obj['key_results']:
                    dashboard.append(f"   └─ {kr['id']}: {kr['title']}")

        # Product OKRs
        if 'product' in all_okrs:
            dashboard.append("\n🚀 PRODUCT OKRS\n")
            for obj in all_okrs['product']['objectives']:
                dashboard.append(f"📌 {obj['id']}: {obj['title']}")
                dashboard.append(f"   ↳ Supports: {obj.get('parent_objective', 'N/A')}")
                for kr in obj['key_results']:
                    dashboard.append(f"   └─ {kr['id']}: {kr['title']}")

        # Team OKRs
        if 'teams' in all_okrs:
            dashboard.append("\n👥 TEAM OKRS\n")
            for team_okr in all_okrs['teams']:
                dashboard.append(f"\n{team_okr['team']} Team:")
                for obj in team_okr['objectives']:
                    dashboard.append(f"  📌 {obj['id']}: {obj['title']}")
                    for kr in obj['key_results']:
                        dashboard.append(f"     └─ {kr['id']}: {kr['title']}")

        # Alignment Matrix
        dashboard.append("\n\n📊 ALIGNMENT MATRIX\n")
        dashboard.append("Company → Product → Teams")
        dashboard.append("-" * 40)

        if 'company' in all_okrs and 'product' in all_okrs:
            for c_obj in all_okrs['company']['objectives']:
                dashboard.append(f"\n{c_obj['id']}")
                for p_obj in all_okrs['product']['objectives']:
                    if p_obj.get('parent_objective') == c_obj['id']:
                        dashboard.append(f"  ├─ {p_obj['id']}")
                        if 'teams' in all_okrs:
                            for team_okr in all_okrs['teams']:
                                for t_obj in team_okr['objectives']:
                                    if t_obj.get('parent_objective') == p_obj['id']:
                                        dashboard.append(f"    └─ {t_obj['id']} ({team_okr['team']})")

        return "\n".join(dashboard)
