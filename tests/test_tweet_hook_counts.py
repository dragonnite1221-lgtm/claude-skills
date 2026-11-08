"""Hook generation respects empty requests and retains the template order."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/x-twitter-growth/scripts/tweet_composer.py"
SPEC = importlib.util.spec_from_file_location("tweet_composer", SCRIPT)
COMPOSER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPOSER)


class HookCountTests(unittest.TestCase):
    def cli(self, *args):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--type", "hooks",
                                 "--topic", "testing", *args], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        return result.stdout

    def test_zero_count_returns_empty(self):
        self.assertEqual(COMPOSER.generate_hooks("testing", 0), [])

    def test_negative_counts_return_empty(self):
        for count in (-1, -10, -100):
            with self.subTest(count=count):
                self.assertEqual(COMPOSER.generate_hooks("testing", count), [])

    def test_positive_counts_preserve_prefix(self):
        all_hooks = COMPOSER.generate_hooks("testing", 100)
        self.assertEqual(len(all_hooks), sum(map(len, COMPOSER.HOOK_PATTERNS.values())))
        for count in range(1, len(all_hooks) + 2):
            with self.subTest(count=count):
                self.assertEqual(COMPOSER.generate_hooks("testing", count), all_hooks[:count])

    def test_first_hook_and_metadata(self):
        hook = COMPOSER.generate_hooks("testing", 1)[0]
        self.assertEqual(hook["type"], "listicle")
        self.assertEqual(hook["hook"], "7 testing that changed how I think:")
        self.assertEqual(hook["chars"], len(hook["hook"]))

    def test_default_count_and_large_requests(self):
        self.assertEqual(len(COMPOSER.generate_hooks("testing")), 10)
        self.assertEqual(len(COMPOSER.generate_hooks("testing", 1000000)), 30)

    def test_topics_preserve_output_count(self):
        for topic in ("", "한글", "AI & tools", "multiline\ntopic"):
            with self.subTest(topic=topic):
                self.assertEqual(COMPOSER.generate_hooks(topic, 0), [])
                self.assertEqual(len(COMPOSER.generate_hooks(topic, 5)), 5)

    def test_json_cli_zero_negative_and_positive(self):
        for count in (0, -1, 1, 10, 31):
            with self.subTest(count=count):
                actual = json.loads(self.cli("--count", str(count), "--json"))
                self.assertEqual(actual, COMPOSER.generate_hooks("testing", count))

    def test_human_cli_zero_has_no_hook(self):
        text = self.cli("--count", "0")
        self.assertIn("HOOK IDEAS: testing", text)
        self.assertNotIn("[listicle", text)
        self.assertNotIn("chars)", text)


if __name__ == "__main__":
    unittest.main()
