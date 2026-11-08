"""Explicit CLI direction overrides session config; omitted direction inherits it."""

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "engineering/agenthub/scripts/result_ranker.py"
SPEC = importlib.util.spec_from_file_location("ranker_direction_test", SCRIPT)
RANKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RANKER)


class DirectionTests(unittest.TestCase):
    def evaluate(self, configured=None, extra=(), output="json"):
        branches = [f"hub/synthetic/agent-{number}/attempt-1" for number in (1, 2)]
        stream = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / ".agenthub/sessions/synthetic/config.yaml"
            config.parent.mkdir(parents=True)
            text = 'eval_cmd: "SYNTHETIC_NOT_EXECUTED"\nmetric: score\n'
            if configured is not None:
                text += f"direction: {configured}\n"
            config.write_text(text, encoding="utf-8")
            previous = os.getcwd()
            try:
                os.chdir(directory)
                with contextlib.ExitStack() as stack:
                    stack.enter_context(patch.object(sys, "argv", ["ranker", "--session",
                        "synthetic", "--format", output, *extra]))
                    stack.enter_context(patch.object(RANKER, "get_hub_branches", return_value=branches))
                    stack.enter_context(patch.object(RANKER, "get_diff_stats", return_value={
                        "files_changed": 1, "insertions": 0, "deletions": 0, "net_lines": 0}))
                    stack.enter_context(patch.object(RANKER, "get_worktree_path", side_effect=lambda b: b))
                    stack.enter_context(patch.object(RANKER, "run_eval_in_worktree", side_effect=
                        lambda path, cmd: ("score: " + ("10" if "agent-1" in path else "20"), 0)))
                    stack.enter_context(contextlib.redirect_stdout(stream))
                    RANKER.main()
            finally:
                os.chdir(previous)
        return json.loads(stream.getvalue())["results"] if output == "json" else stream.getvalue()

    def test_configured_higher(self):
        results = self.evaluate("higher")
        self.assertEqual([r["agent"] for r in results], ["agent-2", "agent-1"])
        self.assertEqual([r["delta"] for r in results], [10, 0])

    def test_configured_lower(self):
        self.assertEqual(self.evaluate("lower")[0]["agent"], "agent-1")

    def test_no_direction_defaults_lower(self):
        self.assertEqual(self.evaluate()[0]["agent"], "agent-1")

    def test_cli_lower_overrides_config_higher(self):
        self.assertEqual(self.evaluate("higher", ("--direction", "lower"))[0]["agent"], "agent-1")

    def test_cli_higher_overrides_config_lower(self):
        self.assertEqual(self.evaluate("lower", ("--direction", "higher"))[0]["agent"], "agent-2")

    def test_explicit_baseline(self):
        self.assertEqual([r["delta"] for r in self.evaluate("higher", ("--baseline", "0"))], [20, 10])

    def test_table_shows_configured_direction_and_winner(self):
        output = self.evaluate("higher", output="table")
        self.assertIn("Metric: score (higher is better)", output)
        self.assertIn("Winner: agent-2 (20.0)", output)


if __name__ == "__main__":
    unittest.main()
