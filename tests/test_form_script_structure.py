"""Check generated form structure without executing any browser script."""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "engineering/browser-automation/scripts/form_automation_builder.py"
SPEC = importlib.util.spec_from_file_location("form_builder", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
URL = "https://example.com/form"


def action_calls(tree, name):
    return [node for node in ast.walk(tree) if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "page" and node.func.attr == name]


class FormScriptStructureTests(unittest.TestCase):
    def generate(self, fields):
        script, errors = MODULE.build_form_script(URL, fields)
        self.assertIsNone(errors)
        compile(script, "<generated>", "exec")
        return ast.parse(script)

    def field(self, **updates):
        return {"selector": "#name", "type": "text", "value": "Sample", **updates}

    def test_single_step_actions_are_function_body_statements(self):
        tree = self.generate([self.field()])
        form = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "fill_form")
        calls = action_calls(form, "fill")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].lineno, next(n.lineno for n in form.body if isinstance(n, ast.Expr)
                                             and isinstance(n.value, ast.Await)))

    def test_multistep_functions_are_ordered_and_compile(self):
        tree = self.generate([self.field(step=2), self.field(selector="#first", step=1)])
        names = [n.name for n in tree.body if isinstance(n, ast.AsyncFunctionDef)]
        self.assertEqual(names, ["fill_step_1", "fill_step_2", "main"])

    def test_submit_is_clicked_once_and_waits_inside_main(self):
        tree = self.generate([self.field(), {"selector": "#submit", "type": "click", "is_submit": True}])
        self.assertEqual([ast.literal_eval(call.args[0]) for call in action_calls(tree, "click")], ["#submit"])
        main = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "main")
        self.assertEqual(len(action_calls(main, "click")), 0)
        self.assertEqual(len(action_calls(main, "wait_for_load_state")), 1)

    def test_multistep_next_and_submit_each_click_once(self):
        fields = [self.field(step=1), {"selector": "#next", "type": "click", "step": 1},
                  {"selector": "#submit", "type": "click", "is_submit": True, "step": 2}]
        tree = self.generate(fields)
        self.assertEqual([ast.literal_eval(call.args[0]) for call in action_calls(tree, "click")], ["#next", "#submit"])

    def test_optional_wait_keeps_correct_scope(self):
        tree = self.generate([self.field(wait_after="#ready")])
        form = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "fill_form")
        self.assertEqual(len(action_calls(form, "wait_for_selector")), 1)

    def test_direct_helper_default_indent_is_preserved(self):
        action = MODULE.generate_field_action(self.field())
        self.assertTrue(all(line.startswith(" " * 8) for line in action.splitlines()))

    def test_json_config_keeps_field_data(self):
        fields = [self.field(), {"selector": "#submit", "type": "click", "is_submit": True}]
        config, errors = MODULE.build_form_script(URL, fields, output_format="json")
        self.assertIsNone(errors)
        self.assertEqual(config["fields"], fields)
        self.assertEqual(config["field_count"], 2)
        self.assertEqual(set(config["field_types"]), {"text", "click"})

    def test_cli_stdout_modes_and_help(self):
        fixtures = [[self.field()], [self.field(step=1), self.field(selector="#other", step=2)],
                    [{"selector": "#submit", "type": "click", "is_submit": True}]]
        with tempfile.TemporaryDirectory() as directory:
            for index, fields in enumerate(fixtures):
                path = Path(directory) / f"fields-{index}.json"
                path.write_text(json.dumps(fields))
                before = (path.read_bytes(), path.stat().st_mtime_ns)
                flags = [[], ["--json"]] if index == 0 else [[]]
                for flag in flags:
                    result = subprocess.run([sys.executable, "-B", str(SOURCE), "--url", URL,
                                             "--fields", str(path), *flag], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if flag:
                        self.assertEqual(json.loads(result.stdout)["fields"], fields)
                    else:
                        compile(result.stdout, "<generated-cli>", "exec")
                self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
        help_result = subprocess.run([sys.executable, "-B", str(SOURCE), "--help"], capture_output=True, text=True)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)


if __name__ == "__main__":
    unittest.main()
