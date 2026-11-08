"""Honor JSON output when competitors are provided only by handle."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/x-twitter-growth/scripts/competitor_analyzer.py"
SPEC = importlib.util.spec_from_file_location("competitor_analyzer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CompetitorHandlesJsonTests(unittest.TestCase):
    def run_cli(self, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def expected(self, handles):
        return {"competitors": [asdict(MODULE.CompetitorProfile(handle=h)) for h in handles], "insights": []}

    def test_single_handle_json(self):
        output = self.run_cli("--handles", "alice", "--json")
        self.assertEqual(json.loads(output), self.expected(["@alice"]))

    def test_multiple_normalized_handles_json(self):
        output = self.run_cli("--handles", "alice", "@bob", "carol", "--json")
        self.assertEqual(json.loads(output), self.expected(["@alice", "@bob", "@carol"]))

    def test_json_flag_before_handles(self):
        self.assertEqual(json.loads(self.run_cli("--json", "--handles", "@alice")), self.expected(["@alice"]))

    def test_repeated_json_flag(self):
        self.assertEqual(json.loads(self.run_cli("--json", "--handles", "alice", "--json")), self.expected(["@alice"]))

    def test_duplicate_handles_preserve_existing_policy(self):
        self.assertEqual(json.loads(self.run_cli("--handles", "alice", "alice", "--json")), self.expected(["@alice", "@alice"]))

    def test_human_tutorial_remains_available(self):
        output = self.run_cli("--handles", "alice", "@bob")
        self.assertIn("Handles registered: @alice, @bob", output)
        self.assertIn("To get full analysis, provide data via JSON import:", output)
        self.assertIn("Example JSON:", output)
        self.assertNotIn("COMPETITIVE ANALYSIS REPORT", output)

    def test_import_json_unchanged(self):
        profiles = [MODULE.CompetitorProfile(handle="@measured", followers=1000, avg_likes=50, posts_per_week=14)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profiles.json"
            path.write_text(json.dumps([asdict(p) for p in profiles]))
            output = self.run_cli("--import", str(path), "--json")
        self.assertEqual(json.loads(output), {"competitors": [asdict(p) for p in profiles], "insights": [asdict(i) for i in MODULE.analyze_competitors(profiles)]})

    def test_handles_match_zero_metric_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profiles.json"
            path.write_text(json.dumps(self.expected(["@alice", "@bob"])["competitors"]))
            imported = self.run_cli("--import", str(path), "--json")
        self.assertEqual(self.run_cli("--handles", "alice", "@bob", "--json"), imported)


if __name__ == "__main__":
    unittest.main()
