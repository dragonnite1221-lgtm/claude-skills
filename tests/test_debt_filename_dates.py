"""Public CLI regressions for debt snapshot filename dates."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/tech-debt-tracker/scripts/debt_dashboard.py"
STAMP = 1700000000


class DebtFilenameDateTests(unittest.TestCase):
    def dashboard(self, fixtures, directory_mode=False, output_format="json"):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inputs = root / "inputs"
            inputs.mkdir()
            paths = []
            before = {}
            for name, data, stamp in fixtures:
                path = inputs / name
                path.write_text(json.dumps(data), encoding="utf-8")
                os.utime(path, (stamp, stamp))
                before[path] = (path.read_bytes(), path.stat().st_mtime_ns)
                paths.append(str(path))
            prefix = root / "report"
            args = ["--input-dir", str(inputs)] if directory_mode else paths
            result = subprocess.run(
                [sys.executable, str(SCRIPT), *args, "--output", str(prefix), "--format", output_format],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            report = json.loads(prefix.with_suffix(".json").read_text())
            text = prefix.with_suffix(".txt").read_text() if output_format == "both" else ""
            for path, original in before.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), original)
        return report, text

    def test_us_date_and_leap_day(self):
        for name, expected in [("scan_01-15-2024.json", "2024-01-15"),
                               ("scan_02-29-2024.json", "2024-02-29")]:
            with self.subTest(name=name):
                report, _ = self.dashboard([(name, [], STAMP)])
                self.assertEqual(report["metadata"]["date_range"]["start"], expected + "T12:00:00")

    def test_existing_iso_and_compact_dates(self):
        for name in ("scan_2024-02-29.json", "scan_20240229.json"):
            with self.subTest(name=name):
                report, _ = self.dashboard([(name, [], STAMP)])
                self.assertEqual(report["metadata"]["date_range"]["start"], "2024-02-29T12:00:00")

    def test_invalid_and_absent_dates_use_mtime(self):
        for name in ("scan_02-29-2023.json", "scan_13-01-2024.json", "scan.json"):
            with self.subTest(name=name):
                report, _ = self.dashboard([(name, [], STAMP)])
                self.assertEqual(report["metadata"]["date_range"]["start"],
                                 datetime.fromtimestamp(STAMP).isoformat())

    def test_chronology_uses_filename_not_reverse_mtime(self):
        report, _ = self.dashboard([
            ("scan_02-01-2024.json", [{"type": "todo_comment"}], STAMP),
            ("scan_01-15-2024.json", [], STAMP + 86400),
        ])
        self.assertEqual(report["metadata"]["date_range"],
                         {"start": "2024-01-15T12:00:00", "end": "2024-02-01T12:00:00"})
        self.assertEqual(report["executive_summary"]["total_debt_items"], 1)
        self.assertEqual(report["debt_velocity"][0]["net_change"], 1)

    def test_explicit_metadata_dates_take_precedence(self):
        for data in [
            {"debt_items": [], "scan_metadata": {"scan_date": "2025-03-01T10:00:00"}},
            {"prioritized_backlog": [], "metadata": {"analysis_date": "2025-03-01T10:00:00"}},
        ]:
            with self.subTest(data=data):
                report, _ = self.dashboard([("scan_01-15-2024.json", data, STAMP)])
                self.assertEqual(report["metadata"]["date_range"]["start"], "2025-03-01T10:00:00")

    def test_directory_input_and_both_formats(self):
        report, text = self.dashboard([("scan_12-31-2024.json", [], STAMP)], True, "both")
        self.assertEqual(report["metadata"]["date_range"]["end"], "2024-12-31T12:00:00")
        self.assertIn("Date Range: 2024-12-31 to 2024-12-31", text)


if __name__ == "__main__":
    unittest.main()

