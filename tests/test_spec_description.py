import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/spec-driven-workflow/scripts/spec_generator.py'
spec = importlib.util.spec_from_file_location('spec_generator_description', SCRIPT)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class DescriptionTests(unittest.TestCase):
    def test_multiline_description_and_guidance(self):
        for description in ['First paragraph\n\nSecond paragraph', '- first\n- second', '한국어\nEnglish', '```\n  sample\n```']:
            with self.subTest(description=description):
                context = generator.generate_context_prompt(description)
                self.assertTrue(context.startswith(description + '\n\n_Expand this context'))
                self.assertNotIn('\n            _-', context)

    def test_preserve_supplied_indentation(self):
        for description in ['    code', '\tcode', 'first\n    nested\n  tail', '\nfirst\n']:
            with self.subTest(description=description):
                self.assertTrue(generator.generate_context_prompt(description).startswith(description + '\n\n_Expand'))

    def test_empty_and_json(self):
        self.assertTrue(generator.generate_context_prompt('').startswith('_Why does this feature'))
        description = 'First\n\n  second'
        self.assertEqual(generator.generate_spec_json('Name', description)['spec']['context'], description)

    def test_cli_markdown_context(self):
        description = 'Overview\n\n- first\n  - nested'
        result = subprocess.run([sys.executable, str(SCRIPT), '--name', 'Demo', '--description', description], capture_output=True, text=True, check=True)
        self.assertIn('## Context\n\n' + description + '\n\n_Expand', result.stdout)


if __name__ == '__main__':
    unittest.main()
