"""Generated Python must preserve descriptions as literal docstrings."""

import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "engineering" /
          "mcp-server-builder" / "scripts" / "openapi_to_mcp.py")


class PythonDescriptionTests(unittest.TestCase):
    def generate(self, description, field="summary", file_input=False):
        operation = {"operationId": "read_records", field: description,
                     "responses": {"200": {"description": "OK"}}}
        spec = {"openapi": "3.0.3", "info": {"title": "Fixture", "version": "1"},
                "paths": {"/records": {"get": operation}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = [sys.executable, str(SCRIPT), "--server-name", "fixture",
                       "--language", "python", "--output-dir", str(root / "out"),
                       "--format", "json"]
            payload = json.dumps(spec)
            if file_input:
                source = root / "input.json"
                source.write_text(payload, encoding="utf-8")
                command += ["--input", str(source)]
                payload = None
            result = subprocess.run(command, input=payload, text=True,
                                    capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            summary = json.loads(result.stdout)
            self.assertEqual(summary["tools_generated"], 1)
            manifest = json.loads((root / "out/tool_manifest.json").read_text())
            self.assertEqual(manifest["tools"][0]["description"], description)
            generated = (root / "out/server.py").read_text(encoding="utf-8")
            compile(generated, "server.py", "exec")
            tree = ast.parse(generated)
            functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
            self.assertEqual(len(functions), 1)
            function = functions[0]
            self.assertEqual(function.name, "read_records")
            self.assertEqual(ast.get_docstring(function, clean=False), description)
            self.assertEqual(len(function.body), 2)
            self.assertIsInstance(function.body[1], ast.Return)

    def test_plain_summary(self):
        self.generate("Read records")

    def test_quotes(self):
        self.generate('Read the """quoted""" field and its single \' quote')

    def test_literal_backslashes(self):
        self.generate(r"Path C:\new\tools and literal \u1234")

    def test_trailing_backslash(self):
        self.generate("Ends in " + chr(92))

    def test_control_characters(self):
        self.generate("NUL " + chr(0) + " tab\t CR\r end")

    def test_unicode_multiline_file_description(self):
        self.generate("한글 설명\n  Indented 😀 line\n", field="description", file_input=True)

    def test_statement_like_description_remains_data(self):
        self.generate('"""\n    sentinel = 123\n    """')


if __name__ == "__main__":
    unittest.main()
