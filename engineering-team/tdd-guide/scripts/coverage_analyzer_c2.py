# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402


class CoverageAnalyzerMixin2:
    def calculate_summary(self) -> Dict[str, Any]:
        """
        Calculate overall coverage summary.

        Returns:
            Summary with line, branch, and function coverage percentages
        """
        total_lines = 0
        covered_lines = 0
        total_branches = 0
        covered_branches = 0
        total_functions = 0
        covered_functions = 0

        for file_path, file_data in self.coverage_data.items():
            # Lines
            for line_num, hit_count in file_data.get('lines', {}).items():
                total_lines += 1
                if hit_count > 0:
                    covered_lines += 1

            # Branches
            for branch_id, hit_count in file_data.get('branches', {}).items():
                total_branches += 1
                if hit_count > 0:
                    covered_branches += 1

            # Functions
            for func_name, hit_count in file_data.get('functions', {}).items():
                total_functions += 1
                if hit_count > 0:
                    covered_functions += 1

        summary = {
            'line_coverage': self._safe_percentage(covered_lines, total_lines),
            'branch_coverage': self._safe_percentage(covered_branches, total_branches),
            'function_coverage': self._safe_percentage(covered_functions, total_functions),
            'total_lines': total_lines,
            'covered_lines': covered_lines,
            'total_branches': total_branches,
            'covered_branches': covered_branches,
            'total_functions': total_functions,
            'covered_functions': covered_functions
        }

        self.summary = summary
        return summary
    def _safe_percentage(self, covered: int, total: int) -> float:
        """Safely calculate percentage."""
        if total == 0:
            return 0.0
        return round((covered / total) * 100, 2)
    def identify_gaps(self, threshold: float = 80.0) -> List[Dict[str, Any]]:
        """
        Identify coverage gaps below threshold.

        Args:
            threshold: Minimum acceptable coverage percentage

        Returns:
            List of files with coverage gaps
        """
        gaps = []

        for file_path, file_data in self.coverage_data.items():
            file_gaps = self._analyze_file_gaps(file_path, file_data, threshold)
            if file_gaps:
                gaps.append(file_gaps)

        self.gaps = gaps
        return gaps
    def _analyze_file_gaps(
        self,
        file_path: str,
        file_data: Dict[str, Any],
        threshold: float
    ) -> Optional[Dict[str, Any]]:
        """Analyze coverage gaps for a single file."""
        lines = file_data.get('lines', {})
        branches = file_data.get('branches', {})
        functions = file_data.get('functions', {})

        # Calculate file coverage
        total_lines = len(lines)
        covered_lines = sum(1 for hit in lines.values() if hit > 0)
        line_coverage = self._safe_percentage(covered_lines, total_lines)

        total_branches = len(branches)
        covered_branches = sum(1 for hit in branches.values() if hit > 0)
        branch_coverage = self._safe_percentage(covered_branches, total_branches)

        # Find uncovered lines
        uncovered_lines = [line_num for line_num, hit in lines.items() if hit == 0]
        uncovered_branches = [branch_id for branch_id, hit in branches.items() if hit == 0]

        # Only report if below threshold
        if line_coverage < threshold or branch_coverage < threshold:
            return {
                'file': file_path,
                'line_coverage': line_coverage,
                'branch_coverage': branch_coverage,
                'uncovered_lines': sorted(uncovered_lines),
                'uncovered_branches': uncovered_branches,
                'priority': self._calculate_priority(line_coverage, branch_coverage, threshold)
            }

        return None
