"""Preserve the complete duration estimate when allocating migration phases."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'engineering/migration-architect/scripts/migration_planner.py'
SPEC = importlib.util.spec_from_file_location('migration_phase_duration', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PhaseDurationTests(unittest.TestCase):
    def test_schema_change_preserves_twenty_four_hours(self):
        planner = MODULE.MigrationPlanner()
        plan = planner.generate_plan(dict(type='database', pattern='schema_change', source='a', target='b'))
        self.assertEqual(plan.estimated_duration_hours, 24)
        self.assertEqual([p.duration_hours for p in plan.phases], [5, 5, 5, 5, 4])
        self.assertEqual(sum(p['estimated_time_minutes'] for p in plan.rollback_plan['rollback_phases']), 360)

    def test_all_patterns_and_complexities_preserve_estimate(self):
        planner = MODULE.MigrationPlanner()
        for kind, patterns in planner.migration_patterns.items():
            for pattern in patterns:
                for complexity in ['low', 'medium', 'high', 'critical']:
                    with self.subTest(kind=kind, pattern=pattern, complexity=complexity):
                        planner._calculate_complexity = lambda spec, c=complexity: c
                        plan = planner.generate_plan(dict(type=kind, pattern=pattern, source='a', target='b'))
                        expected = planner._estimate_duration(kind, pattern, complexity)
                        durations = [p.duration_hours for p in plan.phases]
                        self.assertEqual(sum(durations), expected)
                        self.assertEqual(plan.estimated_duration_hours, expected)
                        self.assertLessEqual(max(durations) - min(durations), 1)
                        self.assertTrue(all(type(d) is int for d in durations))
                        self.assertEqual([p.dependencies for p in plan.phases],
                                         [[]] + [[p.name] for p in plan.phases[:-1]])
                        self.assertEqual(sum(p['estimated_time_minutes'] for p in plan.rollback_plan['rollback_phases']), expected * 15)

    def test_cli_json_and_text_report_complete_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'spec.json'
            path.write_text(json.dumps(dict(type='database', pattern='schema_change', source='a', target='b')))
            for fmt in ['json', 'text']:
                result = subprocess.run([sys.executable, str(SCRIPT), '-i', str(path), '-f', fmt],
                                        capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                if fmt == 'json':
                    self.assertEqual(json.loads(result.stdout)['estimated_duration_hours'], 24)
                else:
                    self.assertIn('Estimated Duration: 24 hours', result.stdout)


if __name__ == '__main__':
    unittest.main()
