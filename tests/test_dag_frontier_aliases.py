"""Equal Git tips are aliases, not descendants of one another."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/agenthub/scripts/dag_analyzer.py"


class FrontierAliasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "--quiet")
        self.tree = self.git("mktree", input="")
        self.base = self.commit("base")
        self.git("update-ref", "refs/heads/main", self.base)
        self.git("symbolic-ref", "HEAD", "refs/heads/main")

    def git(self, *args, input=None):
        result = subprocess.run(
            ["git", "-C", str(self.root), "-c", "user.name=Fixture",
             "-c", "user.email=fixture@example.invalid", *args],
            input=input, capture_output=True, text=True, check=True)
        return result.stdout.strip()

    def commit(self, message, parent=None):
        args = ["commit-tree", self.tree, "-m", message]
        if parent:
            args.extend(["-p", parent])
        return self.git(*args)

    def branch(self, agent, commit, session="sample"):
        name = f"hub/{session}/agent-{agent}/attempt-1"
        self.git("update-ref", "refs/heads/" + name, commit)
        return name

    def run_json(self, mode="--frontier", session="sample"):
        args = [sys.executable, str(SCRIPT), mode, "--format", "json"]
        if session is not None:
            args.extend(["--session", session])
        result = subprocess.run(args, cwd=self.root, capture_output=True,
                                text=True, check=True)
        self.assertEqual("", result.stderr)
        return json.loads(result.stdout)

    def test_empty_and_single_tip(self):
        self.assertEqual([], self.run_json()["frontier"])
        branch = self.branch(1, self.base)
        self.assertEqual([branch], self.run_json()["frontier"])

    def test_equal_tip_branches_are_all_frontier(self):
        branches = [self.branch(agent, self.base) for agent in (1, 2, 3)]
        self.assertEqual(branches, self.run_json()["frontier"])

    def test_parent_aliases_are_excluded_when_extended(self):
        self.branch(1, self.base)
        self.branch(2, self.base)
        child = self.commit("child", self.base)
        branch = self.branch(3, child)
        self.assertEqual([branch], self.run_json()["frontier"])

    def test_child_aliases_remain_frontier(self):
        self.branch(1, self.base)
        child = self.commit("child", self.base)
        branches = [self.branch(agent, child) for agent in (2, 3)]
        self.assertEqual(branches, self.run_json()["frontier"])

    def test_divergent_tips_remain_frontier(self):
        left = self.branch(1, self.commit("left", self.base))
        right = self.branch(2, self.commit("right", self.base))
        self.assertEqual([left, right], self.run_json()["frontier"])

    def test_session_filter_preserves_aliases(self):
        one = self.branch(1, self.base)
        two = self.branch(1, self.base, session="other")
        self.assertEqual([one], self.run_json()["frontier"])
        self.assertEqual(sorted([one, two]), self.run_json(session=None)["frontier"])

    def test_status_marks_equal_tips_as_frontier(self):
        branches = [self.branch(agent, self.base) for agent in (1, 2)]
        report = self.run_json("--status")
        self.assertEqual(branches, [a["branch"] for a in report["agents"]])
        self.assertTrue(all(a["frontier"] for a in report["agents"]))
        self.assertTrue(all(a["commits_ahead"] == 0 for a in report["agents"]))


if __name__ == "__main__":
    unittest.main()
