"""Breaking markers must not hide known commit types in Other."""
from pathlib import Path
import runpy
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'product-team/roadmap-communicator/scripts/changelog_generator.py'
MODULE = runpy.run_path(str(SCRIPT))
GROUP = MODULE['group_commits']
TYPES = ['feat', 'fix', 'docs', 'refactor', 'test', 'chore', 'perf', 'ci', 'build', 'style', 'revert']


class BreakingCommitTypesTests(unittest.TestCase):
    cli_count = 0

    def cli(self, *args, stdin=''):
        type(self).cli_count += 1
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), *args],
                                input=stdin, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_all_known_types_and_marker_forms(self):
        for kind in TYPES:
            for suffix in [': change', '(api): change', '!: change', '(api)!: change']:
                with self.subTest(kind=kind, suffix=suffix):
                    subject = kind + suffix
                    self.assertEqual(dict(GROUP([subject])), {kind: [subject]})

    def test_unknown_and_lookalike_types_remain_other(self):
        subjects = ['feature!: change', 'bugfix!: change', 'FEAT!: change',
                    'custom!: change', 'feat!!: change', 'feat! change', 'plain subject']
        self.assertEqual(dict(GROUP(subjects)), {'other': subjects})

    def test_original_subjects_duplicates_and_order_are_preserved(self):
        subjects = ['fix!: first: detail', 'feat!: café 🧪', 'fix(api)!: second',
                    'fix!: first: detail', 'feat: ordinary']
        self.assertEqual(dict(GROUP(subjects)), {
            'fix': [subjects[0], subjects[2], subjects[3]],
            'feat': [subjects[1], subjects[4]],
        })

    def test_cli_markdown_sections(self):
        result = self.cli('--stdin', stdin='fix!: remove old setting\nfeat!: new API\nplain note\n')
        self.assertEqual(result.stderr, '')
        self.assertEqual(result.stdout, '# Changelog\n\n## Features\n- feat!: new API\n\n'
                         '## Fixes\n- fix!: remove old setting\n\n## Other\n- plain note\n')

    def test_cli_text_sections(self):
        result = self.cli('--stdin', '--format', 'text',
                          stdin='fix!: remove old setting\nfeat!: new API\nplain note\n')
        self.assertEqual(result.stderr, '')
        self.assertEqual(result.stdout, 'FEATURES\n* feat!: new API\n\n'
                         'FIXES\n* fix!: remove old setting\n\nOTHER\n* plain note\n')

    def test_demo_retains_all_subjects_in_both_formats(self):
        for output_format in ['markdown', 'text']:
            result = self.cli('--demo', '--format', output_format)
            self.assertEqual(result.stderr, '')
            for subject in MODULE['DEMO_COMMITS']:
                self.assertEqual(result.stdout.count(subject), 1)
            self.assertNotIn('Other', result.stdout)
            self.assertNotIn('OTHER', result.stdout)

    def test_empty_stdin_retains_notice(self):
        result = self.cli('--stdin', stdin='\n \n')
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, 'No commits found.\n')

    def test_help(self):
        result = self.cli('--help')
        self.assertEqual(result.stderr, '')
        self.assertIn('Generate changelog', result.stdout)

    @classmethod
    def tearDownClass(cls):
        print(f'CLI invocations: {cls.cli_count}')


if __name__ == '__main__':
    unittest.main()
