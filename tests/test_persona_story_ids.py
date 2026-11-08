"""Persona stories in one generated epic must have distinct identifiers."""

import copy
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "product-team/agile-product-owner/scripts/user_story_generator.py"
SPEC = importlib.util.spec_from_file_location("story_generator", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PersonaStoryIdentifiersTests(unittest.TestCase):
    def setUp(self):
        self.generator = MODULE.UserStoryGenerator()

    def test_sample_persona_identifiers_are_distinct(self):
        stories = self.generator.generate_epic_stories(MODULE.create_sample_epic())
        identifiers = [story["id"] for story in stories if story["type"] == "story"]
        self.assertEqual(identifiers, [f"USE-{index:03d}" for index in range(1, 11)])

    def test_four_personas_do_not_restart_numbering(self):
        epic = {"name": "Dashboard", "personas": ["end_user", "admin", "power_user", "new_user"],
                "scope": ["View metrics", "Export data", "Share reports"]}
        stories = self.generator.generate_epic_stories(epic)
        self.assertEqual([story["id"] for story in stories], [f"DAS-{index:03d}" for index in range(1, 13)])

    def test_single_persona_payload_is_unchanged(self):
        epic = {"name": "Dashboard", "personas": ["admin"], "scope": ["View metrics", "Export data"]}
        expected = [self.generator.generate_story("admin", feature, "Dashboard", index)
                    for index, feature in enumerate(epic["scope"], 1)]
        self.assertEqual(self.generator.generate_epic_stories(epic), expected)

    def test_non_identifier_fields_and_order_are_preserved(self):
        epic = MODULE.create_sample_epic()
        actual = self.generator.generate_epic_stories(epic)
        expected = [self.generator.generate_story(persona, feature, epic["name"], index)
                    for persona in epic["personas"] for index, feature in enumerate(epic["scope"], 1)]
        expected.extend(self.generator.generate_enabler_story(req, epic["name"])
                        for req in epic["technical_requirements"])
        self.assertEqual([{k: v for k, v in s.items() if k != "id"} for s in actual],
                         [{k: v for k, v in s.items() if k != "id"} for s in expected])

    def test_generation_is_deterministic_and_preserves_input(self):
        epic = MODULE.create_sample_epic()
        before = copy.deepcopy(epic)
        first = self.generator.generate_epic_stories(epic)
        self.assertEqual(first, self.generator.generate_epic_stories(epic))
        self.assertEqual(epic, before)

    def test_empty_personas_or_scope(self):
        for epic in [{"personas": [], "scope": ["View metrics"]}, {"scope": []}]:
            with self.subTest(epic=epic):
                self.assertEqual(self.generator.generate_epic_stories(epic), [])

    def test_sprint_cli_labels_persona_stories_uniquely(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE), "sprint", "100"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        identifiers = re.findall(r"\] (USE-\d+):", result.stdout)
        self.assertEqual(sorted(identifiers), [f"USE-{index:03d}" for index in range(1, 11)])

    def test_default_cli_still_renders_sample(self):
        result = subprocess.run([sys.executable, "-B", str(SOURCE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Generated 12 stories", result.stdout)
        self.assertIn("Total Stories: 12", result.stdout)


if __name__ == "__main__":
    unittest.main()
