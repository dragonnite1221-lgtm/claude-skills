"""Regression checks for wiki log-gap reporting."""

import contextlib
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/llm-wiki/scripts/lint_wiki.py"
SPEC = importlib.util.spec_from_file_location("wiki_log_gap", SCRIPT)
LINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINT)
NO_ENTRIES = {"last_entry": None, "days_ago": None}


class FixedDate(dt.date):
    @classmethod
    def today(cls):
        return cls(2026, 11, 8)


class WikiLogGapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name)
        (self.vault / "wiki").mkdir()
        self.log = self.vault / "wiki/log.md"

    def scan(self, days=14):
        with patch.object(LINT.dt, "date", FixedDate):
            return LINT.scan(self.vault, 90, days)

    def test_missing_log_matches_empty_log(self):
        missing = self.scan()
        self.assertEqual(missing["log_gap"], NO_ENTRIES)
        self.assertFalse(self.log.exists())
        self.log.write_text("", encoding="utf-8")
        self.assertEqual(missing, self.scan())

    def test_heading_only_log_has_no_entries(self):
        self.log.write_text("# Wiki log\nNo entries yet.\n", encoding="utf-8")
        self.assertEqual(self.scan()["log_gap"], NO_ENTRIES)

    def test_recent_threshold_and_stale_dates(self):
        for age in [-1, 0, 13, 14, 15, 100]:
            with self.subTest(age=age):
                date = (FixedDate.today() - dt.timedelta(days=age)).isoformat()
                self.log.write_text(f"## [{date}] Entry\n", encoding="utf-8")
                expected = {"last_entry": date, "days_ago": age} if age > 14 else None
                self.assertEqual(self.scan()["log_gap"], expected)

    def test_latest_entry_and_custom_threshold(self):
        self.log.write_text("## [2026-10-01] Old\n## [2026-11-06] New\n", encoding="utf-8")
        self.assertIsNone(self.scan(days=2)["log_gap"])
        self.assertEqual(self.scan(days=1)["log_gap"], {"last_entry": "2026-11-06", "days_ago": 2})

    def test_missing_log_human_report_warns(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            LINT.print_report(self.scan())
        self.assertIn("[WARN] log gap:", out.getvalue())
        self.assertNotIn("[OK] log gap: recent", out.getvalue())

    def test_pages_and_existing_log_are_unchanged(self):
        page = self.vault / "wiki/example.md"
        page.write_text("---\ntitle: Example\ncategory: concept\nsummary: Test\n---\n", encoding="utf-8")
        self.log.write_text("## [2026-11-08] Entry\n", encoding="utf-8")
        before = {p: p.read_bytes() for p in [page, self.log]}
        report = self.scan()
        self.assertEqual(report["total_pages"], 1)
        self.assertEqual(report["orphans"], ["example"])
        self.assertEqual(report["missing_frontmatter"], [])
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_missing_log_cli_json_and_human(self):
        for flags in [("--json",), ()]:
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--vault", str(self.vault), *flags], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            if flags:
                self.assertEqual(json.loads(result.stdout)["log_gap"], NO_ENTRIES)
            else:
                self.assertIn("[WARN] log gap:", result.stdout)
            self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
