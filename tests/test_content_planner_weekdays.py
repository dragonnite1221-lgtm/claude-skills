"""Apply posting rules to calendar weekdays for arbitrary start dates."""

from datetime import datetime, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/x-twitter-growth/scripts/content_planner.py"
SPEC = importlib.util.spec_from_file_location("content_planner", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ContentPlannerWeekdayTests(unittest.TestCase):
    def check_plan(self, start, frequency=3, weeks=1):
        plans = MODULE.generate_plan("engineering", frequency, weeks, start)
        for index, week in enumerate(plans):
            first = start + timedelta(weeks=index)
            self.assertEqual(week["start_date"], first.strftime("%Y-%m-%d"))
            self.assertEqual(week["end_date"], (first + timedelta(days=6)).strftime("%Y-%m-%d"))
            total = threads = 0
            for offset, day in enumerate(week["days"]):
                date = first + timedelta(days=offset)
                weekday = date.weekday()
                weekend = weekday >= 5
                count = max(1, frequency - int(weekend))
                self.assertEqual(day["date"], date.strftime("%Y-%m-%d"))
                self.assertEqual(day["day_of_week"], date.strftime("%A"))
                self.assertEqual(len(day["posts"]), count)
                self.assertEqual(day["engagement_target"], "15 min reply session" if weekend else "30 min reply session")
                times = MODULE.OPTIMAL_TIMES["weekend" if weekend else "weekday"]
                for position, post in enumerate(day["posts"]):
                    self.assertEqual(post["time"], times[position % len(times)])
                    if weekday in (1, 3) and position == 0:
                        expected = "thread"
                    elif position == count - 1 and not weekend:
                        expected = "question"
                    elif weekday == 4 and position == 0:
                        expected = "quote_tweet"
                    else:
                        expected = "atomic_tweet"
                    self.assertEqual(post["format"], expected)
                    threads += post["format"] == "thread"
                total += count
            self.assertEqual(week["total_posts"], total)
            self.assertEqual(week["thread_count"], threads)
        return plans

    def test_saturday_start(self):
        self.check_plan(datetime(2026, 11, 7))

    def test_wednesday_start(self):
        self.check_plan(datetime(2026, 11, 11))

    def test_all_start_weekdays(self):
        for offset in range(7):
            with self.subTest(offset=offset):
                self.check_plan(datetime(2026, 11, 9) + timedelta(days=offset))

    def test_year_boundary_multiple_weeks(self):
        self.check_plan(datetime(2026, 12, 30), weeks=3)

    def test_leap_day_boundary(self):
        self.check_plan(datetime(2028, 2, 26), weeks=2)

    def test_frequencies_preserve_precedence(self):
        for frequency in (1, 2, 5):
            self.check_plan(datetime(2026, 11, 7), frequency=frequency)

    def test_json_cli_matches_calendar_rules(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--niche", "engineering", "--frequency", "3", "--weeks", "1", "--start", "2026-11-07", "--json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.check_plan(datetime(2026, 11, 7)))

    def test_human_cli_uses_weekend_window(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--niche", "engineering", "--weeks", "1", "--start", "2026-11-07"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        saturday = result.stdout.split("2026-11-07", 2)[-1].split("Sunday", 1)[0]
        self.assertIn("09:00-10:00", saturday)
        self.assertIn("15 min reply session", saturday)


if __name__ == "__main__":
    unittest.main()
