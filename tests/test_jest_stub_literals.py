"""Jest display names must be encoded as JavaScript-compatible literals."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "engineering/spec-driven-workflow/scripts/test_extractor.py"
SPEC = importlib.util.spec_from_file_location("extractor_literals", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class JestLiteralTests(unittest.TestCase):
    def generate(self, label):
        ac = {"id": "AC-1", "name": label, "references": ["FR-1"],
              "given": "ready", "when": "submit", "then": ["saved"]}
        ec = {"id": "EC-1", "condition": label, "behavior": "retry"}
        return MODULE.JestGenerator().generate(label, [ac], [ec])

    def labels(self, output):
        lines = output.splitlines()
        calls = [line.strip() for line in lines if line.strip().startswith(("describe(", "it("))]
        return [json.loads(line.split("(", 1)[1].rsplit(", () => {", 1)[0]) for line in calls]

    def test_quotes_backslashes_and_control_characters_roundtrip(self):
        for label in ['Click "Save"', r"C:\new\tests", "line\nnext", "tab\tvalue", "nul\x00value", "한글😀"]:
            with self.subTest(label=label):
                self.assertEqual(self.labels(self.generate(label)),
                                 [label, "AC-1: " + label + " [FR-1]", "EC-1: " + label])

    def test_plain_names_retain_existing_output(self):
        output = self.generate("Simple label")
        self.assertIn('describe("Simple label", () => {', output)
        self.assertIn('it("AC-1: Simple label [FR-1]", () => {', output)
        self.assertEqual(output.count('throw new Error("Not implemented");'), 2)

    def test_markdown_parser_to_generator(self):
        text = '# Spec: Click "Save"\n### AC-1: Open "Settings" (FR-1)\nGiven ready\nWhen clicked\nThen opened\n## Edge Cases\n- EC-1: Missing "file" -> warn\n'
        parser = MODULE.SpecParser(text)
        output = MODULE.JestGenerator().generate(parser.extract_spec_title(), parser.extract_acceptance_criteria(), parser.extract_edge_cases())
        self.assertEqual(self.labels(output), ['Click "Save"', 'AC-1: Open "Settings" [FR-1]', 'EC-1: Missing "file"'])

    def test_cli_generates_encoded_names(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.md"
            path.write_text('# Spec: Say "Hello"\n### AC-1: Save "draft"\nGiven ready\nWhen saved\nThen done\n', encoding="utf-8")
            result = subprocess.run([sys.executable, str(SOURCE), "--file", str(path), "--framework", "jest"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.labels(result.stdout), ['Say "Hello"', 'AC-1: Save "draft"'])


if __name__ == "__main__":
    unittest.main()
