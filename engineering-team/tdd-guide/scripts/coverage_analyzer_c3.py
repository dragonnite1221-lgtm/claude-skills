# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402


class CoverageAnalyzerMixin3:
    def _calculate_priority(
        self,
        line_coverage: float,
        branch_coverage: float,
        threshold: float
    ) -> str:
        """Calculate priority based on coverage gap severity."""
        gap = threshold - min(line_coverage, branch_coverage)

        if gap >= 40:
            return 'P0'  # Critical - less than 40% coverage
        elif gap >= 20:
            return 'P1'  # Important - 60-80% coverage
        else:
            return 'P2'  # Nice to have - 80%+ coverage
    def get_file_coverage(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed coverage information for a specific file.

        Args:
            file_path: Path to file

        Returns:
            Detailed coverage data for file
        """
        if file_path not in self.coverage_data:
            return {}

        file_data = self.coverage_data[file_path]
        lines = file_data.get('lines', {})
        branches = file_data.get('branches', {})
        functions = file_data.get('functions', {})

        total_lines = len(lines)
        covered_lines = sum(1 for hit in lines.values() if hit > 0)

        total_branches = len(branches)
        covered_branches = sum(1 for hit in branches.values() if hit > 0)

        total_functions = len(functions)
        covered_functions = sum(1 for hit in functions.values() if hit > 0)

        return {
            'file': file_path,
            'line_coverage': self._safe_percentage(covered_lines, total_lines),
            'branch_coverage': self._safe_percentage(covered_branches, total_branches),
            'function_coverage': self._safe_percentage(covered_functions, total_functions),
            'lines': lines,
            'branches': branches,
            'functions': functions
        }
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate prioritized recommendations for improving coverage.

        Returns:
            List of recommendations with priority and actions
        """
        recommendations = []

        # Check overall coverage
        summary = self.summary or self.calculate_summary()

        if summary['line_coverage'] < 80:
            recommendations.append({
                'priority': 'P0',
                'type': 'overall_coverage',
                'message': f"Overall line coverage ({summary['line_coverage']}%) is below 80% threshold",
                'action': 'Focus on adding tests for critical paths and business logic',
                'impact': 'high'
            })

        if summary['branch_coverage'] < 70:
            recommendations.append({
                'priority': 'P0',
                'type': 'branch_coverage',
                'message': f"Branch coverage ({summary['branch_coverage']}%) is below 70% threshold",
                'action': 'Add tests for conditional logic and error handling paths',
                'impact': 'high'
            })

        # File-specific recommendations
        for gap in self.gaps:
            if gap['priority'] == 'P0':
                recommendations.append({
                    'priority': 'P0',
                    'type': 'file_coverage',
                    'file': gap['file'],
                    'message': f"Critical coverage gap in {gap['file']}",
                    'action': f"Add tests for lines: {gap['uncovered_lines'][:10]}",
                    'impact': 'high'
                })

        # Sort by priority
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return recommendations
