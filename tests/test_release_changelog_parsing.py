"""Release-manager full git logs and conventional breaking footers."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/release-manager/changelog_generator.py"
spec = importlib.util.spec_from_file_location("release_changelog", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def full_log(message, commit_hash="a" * 40, author="Example Author"):
    return (f"commit {commit_hash}\nAuthor: {author}\nDate:   Mon Jan 15 14:30:22 2024 +0000\n\n"
            + "\n".join("    " + line for line in message.split("\n")) + "\n")


class ReleaseChangelogParsingTests(unittest.TestCase):
    def test_full_log_preserves_messages_and_metadata(self):
        generator = module.ChangelogGenerator()
        generator.parse_git_log_output(full_log("feat(api): add endpoint\n\nDescription #12")
                                       + "\n" + full_log("fix(ui): repair view", "b" * 40, "Other Author"))
        self.assertEqual(len(generator.commits), 2)
        first, second = generator.commits
        self.assertEqual((first.type, first.scope, first.description, first.body),
                         ("feat", "api", "add endpoint", "Description #12"))
        self.assertEqual((first.author, first.commit_hash), ("Example Author", "a" * 40))
        self.assertTrue(first.date.startswith("Mon Jan 15"))
        self.assertEqual((second.type, second.description, second.author),
                         ("fix", "repair view", "Other Author"))
        self.assertEqual(first.extract_issue_references(), ["12"])
        self.assertIn("### Added", generator.generate_markdown_changelog())
        self.assertIn("### Fixed", generator.generate_markdown_changelog())

    def test_indented_hash_and_metadata_lookalikes_stay_in_body(self):
        generator = module.ChangelogGenerator()
        body = "deadbee fix: example\ncommit " + "b" * 40 + "\nAuthor: body value\n    nested"
        generator.parse_git_log_output(full_log("fix: retain body\n\n" + body))
        self.assertEqual(len(generator.commits), 1)
        self.assertEqual(generator.commits[0].body, body)
        self.assertEqual(generator.commits[0].author, "Example Author")

    def test_breaking_footer_spellings_from_json(self):
        for marker in ("BREAKING CHANGE", "BREAKING-CHANGE"):
            with self.subTest(marker=marker):
                generator = module.ChangelogGenerator()
                generator.parse_json_commits([{"message": f"fix(api): remove old field\n\n{marker}: Use v2"}])
                commit = generator.commits[0]
                self.assertTrue(commit.is_breaking)
                self.assertEqual(commit.breaking_change_description, "Use v2")
                self.assertEqual(generator.generate_release_summary()["breaking_changes"], 1)
                self.assertIn("### Breaking Changes", generator.generate_markdown_changelog())
                item = json.loads(generator.generate_json_output())["categories"]["Fixed"][0]
                self.assertTrue(item["breaking"])
                self.assertEqual(item["breaking_description"], "Use v2")

    def test_breaking_footer_full_log(self):
        for marker in ("BREAKING CHANGE", "BREAKING-CHANGE"):
            with self.subTest(marker=marker):
                generator = module.ChangelogGenerator()
                generator.parse_git_log_output(full_log(f"feat: new API\n\n{marker}: Migrate callers"))
                self.assertEqual(generator.commits[0].breaking_change_description, "Migrate callers")
                self.assertTrue(generator.commits[0].is_breaking)

    def test_nonbreaking_and_oneline_controls(self):
        for message in ("fix: ordinary", "fix: text\n\nMentions BREAKING CHANGE: only prose"):
            self.assertFalse(module.ConventionalCommit(message).is_breaking)
        self.assertTrue(module.ConventionalCommit("feat!: explicit header").is_breaking)
        generator = module.ChangelogGenerator()
        generator.parse_git_log_output("abc1234 feat: add value\ndef5678 fix: repair value\n")
        self.assertEqual([c.description for c in generator.commits], ["add value", "repair value"])
        self.assertEqual([c.commit_hash for c in generator.commits], ["abc1234", "def5678"])

    def test_cli_full_log_reports(self):
        text = full_log("fix: new protocol\n\nBREAKING CHANGE: Update clients")
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "log.txt"
            source.write_text(text, encoding="utf-8")
            for fmt in ("markdown", "json", "both"):
                with self.subTest(format=fmt):
                    run = subprocess.run([sys.executable, "-B", str(SCRIPT), "--input", str(source),
                                          "--format", fmt, "--summary"], capture_output=True, text=True)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertIn("Update clients", run.stdout)
                    self.assertIn("**Breaking Changes:** 1", run.stdout)
                    self.assertNotIn("No notable changes.", run.stdout)


if __name__ == "__main__":
    unittest.main()
