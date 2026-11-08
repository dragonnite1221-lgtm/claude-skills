"""Code examples must survive heading-to-slide conversion unchanged."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/llm-wiki/scripts/export_marp.py'
SPEC = importlib.util.spec_from_file_location('export_marp', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MarpCodeFenceTests(unittest.TestCase):
    def preserved_block(self, block):
        source = 'Intro\n\n' + block + '\n\n## Outside\nBody'
        for theme in ('default', 'gaia', 'uncover'):
            result = MODULE.to_marp(source, theme)
            self.assertIn(block, result)
            self.assertIn('\n---\n\n## Outside\nBody', result)
            self.assertTrue(result.startswith(MODULE.MARP_HEADER.format(theme=theme)))
        return result

    def test_backtick_and_tilde_code_headings_are_preserved(self):
        for marker, info in [('```', 'markdown'), ('~~~', 'python')]:
            with self.subTest(marker=marker):
                self.preserved_block(marker + info + '\n# Code title\n## Code section\n' + marker)

    def test_indent_and_longer_closing_marker(self):
        for indent in range(4):
            with self.subTest(indent=indent):
                self.preserved_block(' ' * indent + '```md\n## Code\n' + ' ' * indent + '`````\t ')

    def test_short_mismatched_and_nonempty_closers_stay_code(self):
        block = '````markdown\n## First\n```\n## Second\n~~~~\n## Third\n```` note\n## Fourth\n````'
        self.preserved_block(block)

    def test_non_ascii_whitespace_is_not_a_closing_fence(self):
        self.preserved_block('```md\n## One\n```\u00a0\n## Two\n```')

    def test_unclosed_fence_protects_remainder(self):
        block = '~~~text\n# Code title\n## Final code'
        result = MODULE.to_marp('Intro\n\n' + block, 'default')
        self.assertTrue(result.endswith(block + '\n'))
        self.assertNotIn('\n---\n\n## Final code', result)

    def test_initial_non_fence_indentation_remains_outside(self):
        expected = MODULE.MARP_HEADER.format(theme='default') + '```\n\n---\n\n## Actual section\nBody\n'
        for prefix in ('    ', '\t', ' \t'):
            for leading in ('', '\n \n', '---\ntitle: Test\n---\n'):
                with self.subTest(prefix=prefix, leading=leading):
                    self.assertEqual(MODULE.to_marp(leading + prefix + '```\n## Actual section\nBody', 'default'), expected)

    def test_backtick_info_rule_and_tilde_info(self):
        invalid = MODULE.to_marp('Intro\n```bad`info\n## Real heading', 'default')
        self.assertIn('\n---\n\n## Real heading', invalid)
        self.preserved_block('~~~info`ok\n## Code\n~~~')

    def test_plain_headings_frontmatter_and_themes(self):
        text = '---\ntitle: Example\n---\nIntro\n## Slide\nBody'
        for theme in ('default', 'gaia', 'uncover'):
            expected = MODULE.MARP_HEADER.format(theme=theme) + 'Intro\n\n---\n\n## Slide\nBody\n'
            self.assertEqual(MODULE.to_marp(text, theme), expected)
        fenced_title = '```md\n# Example\n```\n# Real title'
        self.assertIn('```md\n# Example\n```', MODULE.to_marp(fenced_title, 'default'))

    def test_cli_single_and_subtree_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            page = vault / 'wiki' / 'guide.md'
            page.parent.mkdir()
            code = '```markdown\n# Literal title\n## Literal section\n```'
            page.write_text('# Guide\n\n' + code + '\n\n## Slide\nBody', encoding='utf-8')
            nested = page.parent / 'nested' / 'example.md'
            nested.parent.mkdir()
            nested.write_text('~~~text\n## More code\n~~~\n## Outside', encoding='utf-8')
            before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in (page, nested)}
            for selected, output, flags in [('wiki/guide.md', 'single', ['--json']), ('wiki', 'subtree', [])]:
                process = subprocess.run([sys.executable, '-B', str(SCRIPT), '--vault', str(vault), '--page', selected,
                    '--out', output, '--theme', 'gaia', *flags], capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                self.assertEqual(process.stderr, '')
                rendered = vault / output / 'guide.marp.md'
                self.assertIn(code, rendered.read_text(encoding='utf-8'))
                self.assertEqual(rendered.read_text(encoding='utf-8'), MODULE.to_marp(page.read_text(encoding='utf-8'), 'gaia'))
                if flags:
                    self.assertEqual(json.loads(process.stdout)['rendered'], ['single/guide.marp.md'])
                else:
                    self.assertIn('~~~text\n## More code\n~~~', (vault / output / 'nested/example.marp.md').read_text())
            for path, initial in before.items():
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), initial)


if __name__ == '__main__':
    unittest.main()
