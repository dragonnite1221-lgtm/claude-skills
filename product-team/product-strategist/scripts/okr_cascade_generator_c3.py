# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from okr_cascade_generator_base import *  # noqa: F403,E402


class OKRGeneratorMixin3:
    def calculate_alignment_score(self, all_okrs: Dict) -> Dict:
        """Calculate alignment score across OKR cascade"""

        scores = {
            'vertical_alignment': 0,
            'horizontal_alignment': 0,
            'coverage': 0,
            'balance': 0,
            'overall': 0
        }

        # Vertical alignment: How well each level supports the above
        total_objectives = 0
        aligned_objectives = 0

        if 'product' in all_okrs:
            for obj in all_okrs['product']['objectives']:
                total_objectives += 1
                if 'parent_objective' in obj:
                    aligned_objectives += 1

        if 'teams' in all_okrs:
            for team in all_okrs['teams']:
                for obj in team['objectives']:
                    total_objectives += 1
                    if 'parent_objective' in obj:
                        aligned_objectives += 1

        if total_objectives > 0:
            scores['vertical_alignment'] = round((aligned_objectives / total_objectives) * 100, 1)

        # Horizontal alignment: How well teams coordinate
        if 'teams' in all_okrs and len(all_okrs['teams']) > 1:
            shared_objectives = set()
            for team in all_okrs['teams']:
                for obj in team['objectives']:
                    parent = obj.get('parent_objective')
                    if parent:
                        shared_objectives.add(parent)

            scores['horizontal_alignment'] = min(100, len(shared_objectives) * 25)

        # Coverage: How much of company OKRs are covered
        if 'company' in all_okrs and 'product' in all_okrs:
            company_krs = sum(len(obj['key_results']) for obj in all_okrs['company']['objectives'])
            covered_krs = sum(len(obj['key_results']) for obj in all_okrs['product']['objectives'])
            if company_krs > 0:
                scores['coverage'] = round((covered_krs / company_krs) * 100, 1)

        # Balance: Distribution across teams
        if 'teams' in all_okrs:
            objectives_per_team = [len(team['objectives']) for team in all_okrs['teams']]
            if objectives_per_team:
                avg_objectives = sum(objectives_per_team) / len(objectives_per_team)
                variance = sum((x - avg_objectives) ** 2 for x in objectives_per_team) / len(objectives_per_team)
                scores['balance'] = round(max(0, 100 - variance * 10), 1)

        # Overall score
        scores['overall'] = round(sum([
            scores['vertical_alignment'] * 0.4,
            scores['horizontal_alignment'] * 0.2,
            scores['coverage'] * 0.2,
            scores['balance'] * 0.2
        ]), 1)

        return scores
    def _get_current_quarter(self) -> str:
        """Get current quarter"""
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        return f"Q{quarter} {now.year}"
    def _fill_metrics(self, template: str, metrics: Dict) -> str:
        """Fill template with actual metrics"""
        result = template
        for key, value in metrics.items():
            result = result.replace(f'{{{key}}}', str(value))
        return result
    def _extract_unit(self, kr_template: str) -> str:
        """Extract measurement unit from KR template"""
        if '%' in kr_template:
            return '%'
        elif '$' in kr_template:
            return '$'
        elif 'days' in kr_template.lower():
            return 'days'
        elif 'score' in kr_template.lower():
            return 'points'
        return 'count'
    def _translate_to_product(self, company_objective: str) -> str:
        """Translate company objective to product objective"""
        translations = {
            'Accelerate user acquisition': 'Build viral product features',
            'Achieve product-market fit': 'Validate product hypotheses',
            'Build sustainable growth': 'Create product-led growth loops',
            'Create lasting customer value': 'Design sticky user experiences',
            'Drive sustainable revenue': 'Optimize product monetization',
            'Lead the market through': 'Ship innovative features to',
            'Improve organizational': 'Improve product delivery'
        }

        for key, value in translations.items():
            if key in company_objective:
                return company_objective.replace(key, value)
        return f"Product: {company_objective}"
