"""Stable engagement is a flat trend, not a decline."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/x-twitter-growth/scripts/growth_tracker.py"
SPEC = importlib.util.spec_from_file_location("growth_tracker", SCRIPT)
GROWTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GROWTH)


def snapshots(rates):
    return [{"timestamp": f"2026-11-{i + 1:02d}T12:00:00", "followers": 100 + i * 10,
             "engagement_rate": rate} for i, rate in enumerate(rates)]


class FlatEngagementTests(unittest.TestCase):
    def report(self, rates):
        return GROWTH.generate_report("@test", snapshots(rates))

    def render(self, report):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            GROWTH.print_report(report)
        return output.getvalue()

    def test_equal_pair_is_flat(self):
        report = self.report([2, 2])
        self.assertEqual(report["engagement_trend"], "flat")
        self.assertEqual(report["avg_engagement_rate"], 2)

    def test_equal_averages_and_odd_counts(self):
        for rates in ([1, 3, 2, 2], [2, 2, 2], [2, 2, 1, 2, 3]):
            with self.subTest(rates=rates):
                self.assertEqual(self.report(rates)["engagement_trend"], "flat")

    def test_improving_and_declining_are_preserved(self):
        for rates, trend, icon in (([1, 2], "improving", "📈"), ([2, 1], "declining", "📉")):
            report = self.report(rates)
            self.assertEqual(report["engagement_trend"], trend)
            self.assertIn(f"{icon} {trend}", self.render(report))

    def test_missing_or_zero_rates_keep_existing_policy(self):
        for rates in ([], [2], [0, 0], [0, 2], [-1, 2]):
            self.assertNotIn("engagement_trend", self.report(rates))
        self.assertEqual(self.report([2, 0, 2])["engagement_trend"], "flat")
        entries = snapshots([2, 2])
        del entries[0]["engagement_rate"]
        self.assertNotIn("engagement_trend", GROWTH.generate_report("@test", entries))

    def test_other_metrics_and_input_are_preserved(self):
        entries = snapshots([2, 2])
        before = copy.deepcopy(entries)
        report = GROWTH.generate_report("@test", entries)
        self.assertEqual(entries, before)
        self.assertEqual((report["follower_change"], report["daily_growth"]), (10, 10))
        self.assertEqual(report["data_points"], 2)

    def test_human_flat_icon(self):
        text = self.render(self.report([2, 2]))
        self.assertIn("Engagement:          ➡️ flat (avg 2.0%)", text)
        self.assertNotIn("📉 declining", text)

    def cli(self, *args):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = root / "scripts/growth_tracker.py"
            script.parent.mkdir()
            shutil.copyfile(SCRIPT, script)
            data = root / ".growth-data"
            data.mkdir()
            (data / "test.jsonl").write_text("\n".join(map(json.dumps, snapshots([2, 2]))))
            result = subprocess.run([sys.executable, "-B", str(script), "--report",
                                     "--handle", "@test", *args], capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stderr), (0, ""))
            return result.stdout

    def test_json_cli(self):
        self.assertEqual(json.loads(self.cli("--json")), self.report([2, 2]))

    def test_human_cli(self):
        self.assertIn("➡️ flat", self.cli())


if __name__ == "__main__":
    unittest.main()
