import copy
from datetime import datetime, timedelta
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/marketing-ops/scripts/campaign_tracker.py"
SPEC = importlib.util.spec_from_file_location("campaign_date_snapshot", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def task(name, deadline, status="in_progress"):
    return {"task": name, "deadline": deadline, "status": status, "owner": "Owner", "skill": "copywriting"}


class DateSnapshotTests(unittest.TestCase):
    def analyze(self, tasks, times):
        clock = Mock()
        clock.now.side_effect = times
        with patch.object(MODULE, "datetime", clock):
            result = MODULE.analyze_campaign({"name": "Synthetic", "tasks": tasks})
        self.assertEqual(clock.now.call_count, 1)
        return result

    def test_equal_deadlines_cannot_cross_different_cutoffs(self):
        start = datetime(2026, 11, 8, 23, 59, 59)
        result = self.analyze([task("A", "2026-11-12"), task("B", "2026-11-12")], [start, start, datetime(2026, 11, 9)])
        self.assertEqual(result["due_soon"], [])

    def test_normal_window_includes_today_through_day_three(self):
        start = datetime(2026, 11, 8, 12)
        tasks = [task(str(offset), (start + timedelta(days=offset)).strftime("%Y-%m-%d")) for offset in (-1, 0, 3, 4)]
        result = self.analyze(tasks, [start] * 10)
        self.assertEqual([t["task"] for t in result["overdue"]], ["-1"])
        self.assertEqual([t["task"] for t in result["due_soon"]], ["0", "3"])

    def test_calendar_rollovers_keep_three_day_window(self):
        for start in (datetime(2026, 12, 30, 23, 59, 59), datetime(2024, 2, 27, 23, 59, 59), datetime(2026, 4, 29, 23, 59, 59)):
            with self.subTest(start=start):
                end = start + timedelta(seconds=1)
                tasks = [task("inside", (start + timedelta(days=3)).strftime("%Y-%m-%d")), task("outside", (start + timedelta(days=4)).strftime("%Y-%m-%d"))]
                result = self.analyze(tasks, [start, end, end])
                self.assertEqual([t["task"] for t in result["due_soon"]], ["inside"])

    def test_completed_tasks_remain_excluded(self):
        start = datetime(2026, 11, 8)
        result = self.analyze([task("old", "2026-11-01", "complete"), task("soon", "2026-11-09", "complete")], [start])
        self.assertEqual(result["overdue"], [])
        self.assertEqual(result["due_soon"], [])
        self.assertEqual(result["progress"], 100)

    def test_input_preserved_and_empty_campaign_supported(self):
        start = datetime(2026, 11, 8)
        tasks = [task("A", "2026-11-10")]
        original = copy.deepcopy(tasks)
        self.analyze(tasks, [start] * 3)
        self.assertEqual(tasks, original)
        result = self.analyze([], [start])
        self.assertEqual((result["total_tasks"], result["progress"]), (0, 0))

    def test_task_order_does_not_change_membership(self):
        start = datetime(2026, 11, 8, 23, 59, 59)
        tasks = [task("A", "2026-11-11"), task("B", "2026-11-12")]
        first = self.analyze(tasks, [start, start, start + timedelta(seconds=1)])
        second = self.analyze(tasks[::-1], [start, start, start + timedelta(seconds=1)])
        self.assertEqual({t["task"] for t in first["due_soon"]}, {t["task"] for t in second["due_soon"]})

    def test_help_cli_still_works(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertIn("input_file", result.stdout)

    def test_demo_cli_still_works(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertIn("CAMPAIGN: Q1 Product Launch", result.stdout)
        self.assertIn("Tasks: 2 done / 2 active / 6 pending", result.stdout)


if __name__ == "__main__":
    unittest.main()
