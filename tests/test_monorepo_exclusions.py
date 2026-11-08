import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "engineering/monorepo-navigator/scripts/monorepo_analyzer.py"
spec = importlib.util.spec_from_file_location("monorepo_exclusions", SCRIPT)
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)


class WorkspaceExclusionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "package.json").write_text('{"name": "root"}', encoding="utf-8")
        for name in ["app", "shared", "legacy"]:
            package = self.root / "packages" / name
            package.mkdir(parents=True)
            data = {"name": "@demo/" + name}
            if name == "app":
                data["dependencies"] = {"@demo/shared": "workspace:*", "@demo/legacy": "*"}
            (package / "package.json").write_text(json.dumps(data), encoding="utf-8")
        (self.root / "packages/empty").mkdir()

    def paths(self, patterns):
        return [str(p.relative_to(self.root)) for p in analyzer.expand_workspace_patterns(self.root, patterns)]

    def test_exclusion_removes_matching_workspace(self):
        self.assertEqual(self.paths(["packages/*", "!packages/legacy"]),
                         ["packages/app", "packages/shared"])

    def test_exclusions_are_order_independent(self):
        for patterns in [["!packages/legacy", "packages/*"],
                         ["packages/*", "!packages/legacy", "packages/legacy"],
                         ["packages/*", "packages/*", "!packages/legacy"]]:
            with self.subTest(patterns=patterns):
                self.assertEqual(self.paths(patterns), ["packages/app", "packages/shared"])

    def test_wildcard_and_normalized_exclusions(self):
        for pattern in ["!packages/l*", "!./packages/legacy", "!packages/../packages/legacy"]:
            with self.subTest(pattern=pattern):
                self.assertEqual(self.paths(["packages/*", pattern]),
                                 ["packages/app", "packages/shared"])
        self.assertEqual(self.paths(["packages/*", "!packages/[ls]*"]), ["packages/app"])

    def test_positive_patterns_and_missing_matches_are_preserved(self):
        self.assertEqual(self.paths(["packages/*"]),
                         ["packages/app", "packages/legacy", "packages/shared"])
        self.assertEqual(self.paths(["packages/app", "packages/app", "!packages/absent"]),
                         ["packages/app"])
        self.assertEqual(self.paths(["!packages/legacy"]), [])
        self.assertEqual(self.paths([]), [])
        self.assertEqual(self.paths(["packages/empty"]), [])

    def test_graph_does_not_include_excluded_package(self):
        workspaces = analyzer.expand_workspace_patterns(self.root, ["packages/*", "!packages/legacy"])
        packages = analyzer.load_workspace_packages(workspaces)
        self.assertEqual(analyzer.build_dependency_graph(packages),
                         {"@demo/app": ["@demo/shared"], "@demo/shared": []})

    def test_pnpm_cli_reports_only_selected_packages(self):
        (self.root / "pnpm-workspace.yaml").write_text(
            "packages:\n  - 'packages/*'\n  - '!packages/legacy'\n", encoding="utf-8")
        for options in [[], ["--json"]]:
            with self.subTest(options=options):
                result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), *options],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                if options:
                    report = json.loads(result.stdout)
                    self.assertEqual(report["workspace_paths"], ["packages/app", "packages/shared"])
                    self.assertEqual(report["package_count"], 2)
                    self.assertEqual(report["dependency_graph"],
                                     {"@demo/app": ["@demo/shared"], "@demo/shared": []})
                else:
                    self.assertNotIn("- packages/legacy", result.stdout.splitlines())
                    self.assertIn("- @demo/app -> @demo/shared", result.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
