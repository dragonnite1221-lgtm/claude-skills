import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'engineering/changelog-generator/scripts/generate_changelog.py'
SPEC = importlib.util.spec_from_file_location('changelog_breaking_under_test', SCRIPT)
GENERATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GENERATOR
SPEC.loader.exec_module(GENERATOR)


class BreakingCommitTests(unittest.TestCase):
    def test_body_footer_sets_major_without_changing_summary(self):
        for marker in ['BREAKING CHANGE:', 'BREAKING-CHANGE:']:
            with self.subTest(marker=marker):
                message = 'fix(api): replace field\n\n' + marker + ' use new field\n'
                commits = GENERATOR.parse_commits([message])
                self.assertEqual(len(commits), 1)
                self.assertEqual(commits[0].summary, 'replace field')
                self.assertEqual(commits[0].scope, 'api')
                self.assertEqual(commits[0].raw, message)
                self.assertEqual(GENERATOR.determine_bump(commits), 'major')

    def test_body_lines_are_not_parsed_as_extra_commits(self):
        message = 'fix: repair parser\n\nfeat: an example in the body\n'
        commits = GENERATOR.parse_commits([message])
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].summary, 'repair parser')
        self.assertEqual(GENERATOR.determine_bump(commits), 'patch')

    def test_prose_mentions_and_invalid_footer_tokens_are_not_breaking(self):
        for body in ['This is not a BREAKING CHANGE.', 'BREAKING CHANGES: none',
                     'BREAKING CHANGE: ', 'breaking change: no', 'not BREAKING CHANGE: no']:
            with self.subTest(body=body):
                commits = GENERATOR.parse_commits(['fix: repair parser\n\n' + body])
                self.assertEqual(len(commits), 1)
                self.assertEqual(GENERATOR.determine_bump(commits), 'patch')

    def test_subject_only_markers_and_empty_input_remain_supported(self):
        for subject, bump in [('feat(api)!: replace API', 'major'),
                              ('fix!: remove field', 'major'), ('feat: add field', 'minor'),
                              ('fix: repair typo', 'patch')]:
            with self.subTest(subject=subject):
                self.assertEqual(GENERATOR.determine_bump(GENERATOR.parse_commits([subject])), bump)
        self.assertEqual(GENERATOR.parse_commits(['', 'not conventional']), [])

    def test_entry_rendering_contains_breaking_summary(self):
        commits = GENERATOR.parse_commits(['feat(api): replace endpoint\n\nBREAKING CHANGE: old route removed'])
        entry = GENERATOR.build_entry(commits, '2.0.0', '2026-11-07')
        self.assertEqual(entry.breaking_changes, ['replace endpoint'])
        self.assertEqual(entry.sections, {'Added': ['api: replace endpoint']})
        self.assertIn('### Breaking\n- replace endpoint', GENERATOR.render_markdown(entry))
        self.assertEqual(entry.bump, 'major')

    def test_git_range_cli_preserves_footer_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1',
                       GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, capture_output=True,
                                      text=True, check=True, env=env).stdout.strip()
            git('init', '-q')
            git('config', 'user.name', 'Test')
            git('config', 'user.email', 'test@example.invalid')
            git('commit', '--allow-empty', '-qm', 'chore: seed')
            start = git('rev-parse', 'HEAD')
            git('commit', '--allow-empty', '-qm', 'fix(api): replace field',
                '-m', 'BREAKING CHANGE: old field removed')
            git('commit', '--allow-empty', '-qm', 'fix: repair parser',
                '-m', 'feat: an example, not another commit')
            result = subprocess.run([sys.executable, str(SCRIPT), '--from-ref', start,
                                     '--to-ref', 'HEAD', '--format', 'json'], cwd=root,
                                    stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True, env=env)
            entry = json.loads(result.stdout)
            self.assertEqual(entry['bump'], 'major')
            self.assertEqual(entry['breaking_changes'], ['replace field'])
            self.assertEqual(entry['sections'], {'Fixed': ['repair parser', 'api: replace field']})


if __name__ == '__main__':
    unittest.main()
