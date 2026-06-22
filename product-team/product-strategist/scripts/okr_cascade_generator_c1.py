# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402


class OKRGeneratorMixin1:
    def generate_company_okrs(self, strategy: str, metrics: Dict) -> Dict:
        """Generate company-level OKRs based on strategy"""

        if strategy not in self.okr_templates:
            strategy = 'growth'

        template = self.okr_templates[strategy]

        company_okrs = {
            'level': 'Company',
            'quarter': self._get_current_quarter(),
            'strategy': strategy,
            'objectives': []
        }

        for i in range(min(3, len(template['objectives']))):
            obj = {
                'id': f'CO-{i+1}',
                'title': template['objectives'][i],
                'key_results': [],
                'owner': 'CEO',
                'status': 'draft'
            }

            for j in range(3):
                if j < len(template['key_results']):
                    kr_template = template['key_results'][j]
                    kr = {
                        'id': f'CO-{i+1}-KR{j+1}',
                        'title': self._fill_metrics(kr_template, metrics),
                        'current': metrics.get('current', 0),
                        'target': metrics.get('target', 100),
                        'unit': self._extract_unit(kr_template),
                        'status': 'not_started'
                    }
                    obj['key_results'].append(kr)

            company_okrs['objectives'].append(obj)

        return company_okrs
    def cascade_to_product(self, company_okrs: Dict) -> Dict:
        """Cascade company OKRs to product organization"""

        product_okrs = {
            'level': 'Product',
            'quarter': company_okrs['quarter'],
            'parent': 'Company',
            'contribution': self.product_contribution,
            'objectives': []
        }

        for company_obj in company_okrs['objectives']:
            product_obj = {
                'id': f'PO-{company_obj["id"].split("-")[1]}',
                'title': self._translate_to_product(company_obj['title']),
                'parent_objective': company_obj['id'],
                'key_results': [],
                'owner': 'Head of Product',
                'status': 'draft'
            }

            for kr in company_obj['key_results']:
                product_kr = {
                    'id': f'PO-{product_obj["id"].split("-")[1]}-KR{kr["id"].split("KR")[1]}',
                    'title': self._translate_kr_to_product(kr['title']),
                    'contributes_to': kr['id'],
                    'current': kr['current'],
                    'target': kr['target'] * self.product_contribution,
                    'unit': kr['unit'],
                    'contribution_pct': self.product_contribution * 100,
                    'status': 'not_started'
                }
                product_obj['key_results'].append(product_kr)

            product_okrs['objectives'].append(product_obj)

        return product_okrs
