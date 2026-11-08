"""Roadmap scoring must not rewrite input controls or earlier results."""
import copy
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'c-level-advisor/ciso-advisor/scripts/compliance_tracker.py'
SPEC = importlib.util.spec_from_file_location('compliance_roadmap_tool', PATH)
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


def controls():
    return [
        {'domain_id': 'a', 'frameworks_applicable': ['soc2', 'iso27001'],
         'effort_days': 5, 'status': 'Not Started'},
        {'domain_id': 'b', 'frameworks_applicable': ['soc2'],
         'effort_days': 8, 'status': 'In Progress'},
        {'domain_id': 'c', 'frameworks_applicable': ['iso27001'],
         'effort_days': 1, 'status': 'Verified'},
    ]


class RoadmapIsolationTests(unittest.TestCase):
    def test_input_unchanged(self):
        source = controls()
        before = copy.deepcopy(source)
        TOOL.estimate_roadmap(source, ['soc2'])
        self.assertEqual(source, before)

    def test_existing_priority_not_overwritten(self):
        source = controls()
        source[0]['_priority_score'] = 123
        result = TOOL.estimate_roadmap(source, ['soc2'])
        self.assertEqual(source[0]['_priority_score'], 123)
        self.assertEqual(result[0]['_priority_score'], 5)

    def test_previous_result_stable(self):
        source = controls()
        first = TOOL.estimate_roadmap(source, ['soc2'])
        before = copy.deepcopy(first)
        second = TOOL.estimate_roadmap(source, ['soc2', 'iso27001'])
        self.assertEqual(first, before)
        self.assertEqual(second[0]['_priority_score'], 15)

    def test_score_and_order(self):
        result = TOOL.estimate_roadmap(controls(), ['soc2'])
        self.assertEqual([(c['domain_id'], c['_priority_score']) for c in result], [('a', 5), ('b', 2)])

    def test_completed_controls_excluded(self):
        source = controls()
        source[0]['status'] = 'Implemented'
        self.assertEqual(TOOL.estimate_roadmap(source, ['iso27001']), [])

    def test_empty_target(self):
        source = controls()
        self.assertEqual(TOOL.estimate_roadmap(source, []), [])
        self.assertEqual(source, controls())

    def test_empty_input(self):
        self.assertEqual(TOOL.estimate_roadmap([], ['soc2']), [])

    def test_sample_input_preserved(self):
        source = TOOL.load_control_library()
        before = copy.deepcopy(source)
        result = TOOL.estimate_roadmap(source, list(TOOL.FRAMEWORKS))
        self.assertTrue(result)
        self.assertEqual(source, before)
        self.assertTrue(all(c is not original for c in result for original in source))


if __name__ == '__main__':
    unittest.main()
