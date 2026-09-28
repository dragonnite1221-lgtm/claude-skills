"""Required failures cannot be hidden by a high quality score."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/required-skill-checks.py"
SPEC = importlib.util.spec_from_file_location("required_skill_checks", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RequiredSkillChecksTest(unittest.TestCase):
    def test_required_failures_block(self):
        structure = {"overall_score": 95, "compliance_level": "EXCELLENT", "checks": {"required": {"passed": True}}, "errors": []}
        scripts = {"summary": {"total_scripts": 1, "passed": 1, "partial": 0, "failed": 0, "overall_status": "PASS"}, "global_errors": []}
        security = {"verdict": "PASS", "summary": {"critical": 0, "high": 0}}
        with tempfile.TemporaryDirectory() as root:
            skill = Path(root)
            (skill / "scripts").mkdir()
            (skill / "scripts/test.py").touch()
            for results, expected in (
                ([(0, structure), (0, scripts), (0, security)], "PASS"),
                ([(0, {**structure, "checks": {"required": {"passed": False}}}), (0, scripts), (0, security)], "FAIL"),
                ([(0, structure), (0, {**scripts, "summary": {**scripts["summary"], "partial": 1, "overall_status": "PARTIAL"}}), (0, security)], "FAIL"),
                ([(0, structure), (0, scripts), (1, {"verdict": "WARN", "summary": {"critical": 0, "high": 1}})], "FAIL"),
            ):
                with self.subTest(expected=expected, results=results), patch.object(MODULE, "run_json", side_effect=results):
                    self.assertEqual(MODULE.evaluate(str(skill))[-1], expected)


if __name__ == "__main__":
    unittest.main()
