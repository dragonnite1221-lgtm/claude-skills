import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'engineering-team/tdd-guide/scripts/coverage_analyzer.py'
spec = importlib.util.spec_from_file_location('coverage_branch_test', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def report(covered, total):
    return f'<coverage><packages><package><classes><class filename="sample.py"><lines><line number="7" hits="1" branch="true" condition-coverage="50% ({covered}/{total})"/></lines></class></classes></package></packages></coverage>'


class BranchTests(unittest.TestCase):
    def test_partial_branch_summary(self):
        analyzer = module.CoverageAnalyzer()
        analyzer.parse_coverage_report(report(1, 2), 'xml')
        summary = analyzer.calculate_summary()
        self.assertEqual(summary['total_branches'], 2)
        self.assertEqual(summary['covered_branches'], 1)
        self.assertEqual(summary['branch_coverage'], 50)

    def test_complete_and_uncovered(self):
        for covered in [0, 2]:
            with self.subTest(covered=covered):
                analyzer = module.CoverageAnalyzer()
                analyzer.parse_coverage_report(report(covered, 2), 'cobertura')
                self.assertEqual(analyzer.calculate_summary()['total_branches'], 2)
                self.assertEqual(analyzer.calculate_summary()['branch_coverage'], covered * 50)

    def test_gap_preserves_uncovered_count(self):
        analyzer = module.CoverageAnalyzer()
        analyzer.parse_coverage_report(report(1, 3), 'xml')
        gaps = analyzer.identify_gaps()
        self.assertEqual(len(gaps), 1)
        self.assertEqual(len(gaps[0]['uncovered_branches']), 2)
        self.assertEqual(analyzer.get_file_coverage('sample.py')['branch_coverage'], 33.33)

    def test_zero_total_and_lines(self):
        analyzer = module.CoverageAnalyzer()
        analyzer.parse_coverage_report(report(0, 0), 'xml')
        summary = analyzer.calculate_summary()
        self.assertEqual(summary['total_branches'], 0)
        self.assertEqual(summary['line_coverage'], 100)


if __name__ == '__main__':
    unittest.main()

