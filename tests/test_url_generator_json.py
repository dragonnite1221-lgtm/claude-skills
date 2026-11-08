import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/programmatic-seo/scripts/url_pattern_generator.py"
SPEC = importlib.util.spec_from_file_location("url_generator_json", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class UrlJsonTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], capture_output=True, text=True)

    def config_cli(self, config, before=(), after=("--json",)):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            return self.cli(*before, str(path), *after)

    def parsed(self, result):
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        return json.loads(result.stdout)

    def test_demo_json_is_one_document(self):
        result = self.cli("--json")
        data = self.parsed(result)
        self.assertEqual(set(data), {"config", "urls", "analysis"})
        self.assertEqual(data["analysis"]["total_pages"], 20)
        self.assertEqual(len(data["urls"]), 20)
        self.assertNotIn("Demo mode", result.stdout)

    def test_demo_json_matches_explicit_sample(self):
        self.assertEqual(self.parsed(self.cli("--json")), self.parsed(self.config_cli(MODULE.SAMPLE_CONFIG)))

    def test_default_human_demo_keeps_notice(self):
        result = self.cli()
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertTrue(result.stdout.startswith("[Demo mode — using sample comparison page config]\n"))
        self.assertIn("PROGRAMMATIC SEO", result.stdout)
        self.assertIn("Total Pages: 20", result.stdout)

    def test_explicit_json_uses_config_values(self):
        config = {"template": "{city}", "variables": {"city": ["New York", "Paris"]}, "base_url": "https://example.com/cities"}
        data = self.parsed(self.config_cli(config))
        self.assertEqual(data["config"], config)
        self.assertEqual([x["url"] for x in data["urls"]], ["https://example.com/cities/new-york", "https://example.com/cities/paris"])

    def test_json_flag_before_path(self):
        config = {"template": "{item}", "variables": {"item": ["one"]}}
        self.assertEqual(self.parsed(self.config_cli(config)), self.parsed(self.config_cli(config, before=("--json",), after=())))

    def test_explicit_human_has_no_demo_notice(self):
        config = {"template": "{item}", "variables": {"item": ["one"]}}
        result = self.config_cli(config, after=())
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertNotIn("Demo mode", result.stdout)
        self.assertIn("Total Pages: 1", result.stdout)

    def test_empty_data_json_is_valid(self):
        config = {"template": "{item}", "variables": {"item": []}}
        data = self.parsed(self.config_cli(config))
        self.assertEqual(data["urls"], [])
        self.assertEqual(data["analysis"]["total_pages"], 0)

    def test_unicode_values_round_trip(self):
        config = {"template": "{city}", "variables": {"city": ["서울", "München"]}}
        data = self.parsed(self.config_cli(config))
        self.assertEqual(data["config"], config)
        self.assertEqual([x["slug"] for x in data["urls"]], ["서울", "münchen"])


if __name__ == "__main__":
    unittest.main()
