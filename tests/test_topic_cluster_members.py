"""Keep every counted cluster member in the serialized output."""

from collections import Counter
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/content-strategy/scripts/topic_cluster_mapper.py"
SPEC = importlib.util.spec_from_file_location("topic_clusters", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TopicClusterMemberTests(unittest.TestCase):
    def output(self, topics):
        result = MODULE.build_output(topics, MODULE.build_clusters(topics))
        members = []
        for cluster in result["clusters"]:
            self.assertEqual(cluster["size"], 1 + len(cluster["supporting_topics"]))
            members.extend([cluster["pillar_topic"], *cluster["supporting_topics"]])
        self.assertEqual(Counter(members), Counter(topics))
        return result

    def test_duplicate_pillar_remains_counted(self):
        result = self.output(["email marketing", "email marketing"])
        self.assertEqual(result["clusters"][0]["supporting_topics"], ["email marketing"])

    def test_multiple_duplicate_pillars(self):
        result = self.output(["email marketing"] * 4)
        self.assertEqual(result["clusters"][0]["supporting_topics"], ["email marketing"] * 3)

    def test_middle_pillar_removes_only_first_occurrence(self):
        topics = ["email strategy", "email automation", "email automation"]
        result = self.output(topics)
        self.assertEqual(result["clusters"][0]["pillar_topic"], "email automation")
        self.assertEqual(result["clusters"][0]["supporting_topics"], ["email strategy", "email automation"])

    def test_duplicate_supporting_members_keep_order(self):
        topics = ["email marketing strategy", "email strategy", "email strategy", "email marketing"]
        clusters = [{"pillar": topics[0], "topics": topics.copy(), "stems": {"email"}}]
        before = copy.deepcopy(clusters)
        result = MODULE.build_output(topics, clusters)
        self.assertEqual(result["clusters"][0]["supporting_topics"], topics[1:])
        self.assertEqual(clusters, before)

    def test_multiple_clusters_and_empty_stems(self):
        self.output(["email marketing", "email marketing", "garden tools", "garden tools", "the", "the"])

    def test_unique_demo_and_singleton(self):
        self.output(MODULE.DEMO_TOPICS)
        self.assertEqual(self.output(["email marketing"])["clusters"][0]["supporting_topics"], [])

    def test_json_cli_preserves_repeated_lines(self):
        topics = ["email marketing", "email marketing", "email automation"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keywords.txt"
            path.write_text("\n".join(topics) + "\n")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--file", str(path), "--json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.output(topics))

    def test_human_cli_lists_the_counted_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keywords.txt"
            path.write_text("email marketing\nemail marketing\n")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--file", str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(2 topics)", result.stdout)
        self.assertIn("Supporting: email marketing", result.stdout)


if __name__ == "__main__":
    unittest.main()
