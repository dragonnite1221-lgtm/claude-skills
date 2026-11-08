"""Read board posts in sequence order across filename padding boundaries."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/agenthub/scripts/board_manager.py"
SPEC = importlib.util.spec_from_file_location("board_post_order", SCRIPT)
BOARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOARD)


class BoardPostOrderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.board = self.root / ".agenthub/board"
        self.channel = self.board / "results"
        self.channel.mkdir(parents=True)
        self.board_patch = patch.object(BOARD, "BOARD_PATH", str(self.board))
        self.board_patch.start()
        self.addCleanup(self.board_patch.stop)

    def add_post(self, number, author="agent-1"):
        name = f"{number:03d}-{author}-20261108T070000Z.md"
        (self.channel / name).write_text(f"---\nauthor: {author}\nsequence: {number}\n---\n\nMessage {number}\n", encoding="utf-8")
        return name

    def read(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            BOARD.read_channel("results", "json")
        return json.loads(out.getvalue())["posts"]

    def test_numeric_order_across_padding_boundaries(self):
        numbers = [10000, 999, 1000, 99, 100, 1, 9999, 101]
        for number in numbers:
            self.add_post(number)
        self.assertEqual([int(p["metadata"]["sequence"]) for p in self.read()], sorted(numbers))

    def test_create_then_read_round_trip(self):
        (self.board / "_index.json").write_text(json.dumps({"channels": ["results"], "counters": {"results": 998}}))
        with contextlib.redirect_stdout(io.StringIO()):
            BOARD.create_post("results", "agent-1", "Earlier")
            BOARD.create_post("results", "agent-1", "Later")
        self.assertEqual([p["body"] for p in self.read()], ["Earlier", "Later"])

    def test_same_sequence_uses_filename_tiebreak(self):
        names = [self.add_post(1000, "z"), self.add_post(1000, "a"), self.add_post(1000, "m")]
        self.assertEqual([p["file"] for p in self.read()], sorted(names))

    def test_unsequenced_posts_follow_numeric_posts(self):
        names = ["notes.md", "agent-2-result.md", "²-summary.md"]
        for name in names:
            (self.channel / name).write_text("Manual post", encoding="utf-8")
        numbered = self.add_post(9999)
        self.assertEqual([p["file"] for p in self.read()], [numbered] + sorted(names))

    def test_non_markdown_files_are_ignored(self):
        (self.channel / "000-ignore.txt").write_text("Ignore")
        self.add_post(1000)
        self.assertEqual(len(self.read()), 1)

    def test_empty_channel(self):
        self.assertEqual(self.read(), [])

    def test_read_preserves_contents_and_mtimes(self):
        for number in [999, 1000]:
            self.add_post(number)
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.channel.iterdir()}
        self.read()
        self.assertEqual(before, {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.channel.iterdir()})

    def test_cli_json_and_text_order(self):
        early = self.add_post(999)
        late = self.add_post(1000)
        for fmt in ["json", "text"]:
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--read", "results", "--format", fmt], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            if fmt == "json":
                self.assertEqual([p["file"] for p in json.loads(result.stdout)["posts"]], [early, late])
            else:
                self.assertLess(result.stdout.index(early), result.stdout.index(late))


if __name__ == "__main__":
    unittest.main()
