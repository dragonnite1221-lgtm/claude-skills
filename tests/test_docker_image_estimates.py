"""Base estimates must select the configured image family and variant."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "engineering" /
          "docker-development" / "scripts" / "dockerfile_analyzer.py")


class ImageEstimateTests(unittest.TestCase):
    def report(self, image, output="json", prefix=""):
        content = prefix + "FROM " + image + '\nUSER app\nHEALTHCHECK CMD true\nCMD ["app"]\n'
        with tempfile.TemporaryDirectory() as directory:
            dockerfile = Path(directory) / "Dockerfile"
            dockerfile.write_text(content, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(dockerfile),
                                     "--output", output], text=True,
                                    capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if output == "json" else result.stdout

    def test_node_alpine(self):
        self.assertEqual(self.report("node:20-alpine")["base_image"]["estimated_size_mb"], 130)

    def test_python_slim(self):
        self.assertEqual(self.report("python:3.12-slim")["base_image"]["estimated_size_mb"], 130)

    def test_other_known_variants(self):
        for image, expected in [("python:3.12-alpine", 50), ("golang:1.22-alpine", 250),
                                ("rust:1.77-slim", 750), ("nginx:1.25-alpine", 40),
                                ("debian:bookworm-slim", 80), ("node:20-slim", 200)]:
            with self.subTest(image=image):
                self.assertEqual(self.report(image)["base_image"]["estimated_size_mb"], expected)

    def test_plain_family_controls(self):
        for image, expected in [("alpine:3.19", 7), ("node:20", 1000),
                                ("python:3.12", 900), ("scratch", 0)]:
            with self.subTest(image=image):
                self.assertEqual(self.report(image)["base_image"]["estimated_size_mb"], expected)

    def test_unknown_family_does_not_borrow_alpine_estimate(self):
        self.assertEqual(self.report("custom:1-alpine")["base_image"]["estimated_size_mb"], 0)

    def test_unsupported_variant_falls_back_to_family(self):
        self.assertEqual(self.report("ubuntu:slim")["base_image"]["estimated_size_mb"], 78)

    def test_namespaced_final_stage(self):
        result = self.report("example.com/team/python:3.12-slim AS runtime",
                             prefix="FROM golang:1.22 AS build\nRUN echo build\n")
        self.assertEqual(result["base_image"]["estimated_size_mb"], 130)
        self.assertEqual(result["base_image"]["image"], "example.com/team/python")
        self.assertEqual(result["base_image"]["tag"], "3.12-slim")
        self.assertEqual(result["layers"]["stages"], 2)

    def test_text_output_uses_correct_estimate(self):
        self.assertIn("Base: node:20-alpine (~130MB)", self.report("node:20-alpine", "text"))


if __name__ == "__main__":
    unittest.main()
