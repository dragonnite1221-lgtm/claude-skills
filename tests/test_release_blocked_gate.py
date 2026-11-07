"""Required blocked quality gates must block the release assessment."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/release-manager/release_planner.py"
spec = importlib.util.spec_from_file_location("release_blocked_gate", SCRIPT)
planner_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = planner_module
spec.loader.exec_module(planner_module)


def plan(status="blocked", required=True):
    return {
        "release_name": "Gate regression", "version": "1.2.3",
        "features": [{"id": "F1", "title": "Ready feature", "status": "ready",
                      "pm_approved": True, "qa_approved": True}],
        "quality_gates": [{"name": "Integration tests", "status": status,
                           "required": required}],
    }


def assess(data):
    planner = planner_module.ReleasePlanner()
    planner.load_release_plan(data)
    return planner, planner.assess_release_readiness()


class BlockedGateTests(unittest.TestCase):
    def test_required_blocked_gate_blocks(self):
        data = plan()
        original = copy.deepcopy(data)
        planner, result = assess(data)
        self.assertEqual(result["overall_status"], "blocked")
        self.assertEqual(result["blocking_issues"],
                         ["Required quality gate 'Integration tests' is blocked"])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["quality_gate_summary"],
                         dict(total=1, passed=0, failed=0, pending=1, required_failed=0))
        self.assertAlmostEqual(result["readiness_score"], 100 * 10 / 15)
        gate = next(x for x in planner.generate_release_checklist() if x["item"] == "Integration tests")
        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(data, original)

    def test_all_gate_statuses_and_required_flag(self):
        required_status = {"pending": "at_risk", "in_progress": "at_risk",
                           "ready": "ready", "blocked": "blocked", "failed": "blocked"}
        for status, expected in required_status.items():
            for required in (True, False):
                with self.subTest(status=status, required=required):
                    _, result = assess(plan(status, required))
                    self.assertEqual(result["overall_status"], expected if required else "ready")
                    self.assertEqual(bool(result["blocking_issues"]),
                                     required and status in ("blocked", "failed"))
                    self.assertEqual(bool(result["warnings"]),
                                     required and status in ("pending", "in_progress"))

    def test_blocked_gate_takes_precedence_over_pending(self):
        data = plan()
        data["quality_gates"].append({"name": "Docs", "status": "pending"})
        _, result = assess(data)
        self.assertEqual(result["overall_status"], "blocked")
        self.assertEqual(result["warnings"], ["Required quality gate 'Docs' is pending"])
        self.assertEqual(len(result["blocking_issues"]), 1)

    def test_cli_formats_and_report_file(self):
        with tempfile.TemporaryDirectory() as folder:
            input_path = Path(folder) / "plan.json"
            input_path.write_text(json.dumps(plan()), encoding="utf-8")
            for output_format in ("json", "text", "markdown"):
                for to_file in (False, True):
                    with self.subTest(format=output_format, file=to_file):
                        args = [sys.executable, "-B", str(SCRIPT), "--input", str(input_path),
                                "--output-format", output_format, "--include-checklist"]
                        report = Path(folder) / "report.txt"
                        if to_file:
                            args.extend(["--output", str(report)])
                        result = subprocess.run(args, capture_output=True, text=True, check=False)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        body = report.read_text(encoding="utf-8") if to_file else result.stdout
                        if output_format == "json":
                            self.assertEqual(json.loads(body)["assessment"]["overall_status"], "blocked")
                        else:
                            self.assertIn("BLOCKED", body)
                        self.assertIn("Required quality gate 'Integration tests' is blocked", body)


if __name__ == "__main__":
    unittest.main()
