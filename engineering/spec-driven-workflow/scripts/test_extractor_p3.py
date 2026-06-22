# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_extractor_base import *  # noqa: F403,E402
# fmt: off
from test_extractor_p1 import _sanitize_name  # noqa: E402,E501
from test_extractor_p2 import JestGenerator, PytestGenerator, _to_pascal_case  # noqa: E402,E501
# fmt: on


class GoTestGenerator:
    """Generates Go test stubs."""

    def generate(self, title: str, criteria: List[Dict], edge_cases: List[Dict]) -> str:
        package_name = _sanitize_name(title).split("_")[0] or "feature"

        lines = [
            f"package {package_name}_test",
            "",
            "import (",
            '\t"testing"',
            ")",
            "",
            f"// Test suite for: {title}",
            f"// Auto-generated from spec. {len(criteria)} acceptance criteria, {len(edge_cases)} edge cases.",
            f"// All tests are stubs — implement the test body to make them pass.",
            "",
        ]

        for ac in criteria:
            func_name = "Test" + _to_pascal_case(ac["id"] + " " + ac["name"])
            ref_str = f" [{', '.join(ac['references'])}]" if ac["references"] else ""

            lines.append(f"// {ac['id']}: {ac['name']}{ref_str}")
            lines.append(f"func {func_name}(t *testing.T) {{")

            if ac["given"]:
                lines.append(f"\t// Given {ac['given']}")
            if ac["when"]:
                lines.append(f"\t// When {ac['when']}")
            for then_clause in ac["then"]:
                lines.append(f"\t// Then {then_clause}")

            lines.append("")
            lines.append('\tt.Fatal("Not implemented")')
            lines.append("}")
            lines.append("")

        if edge_cases:
            lines.append("// --- Edge Cases ---")
            lines.append("")

        for ec in edge_cases:
            func_name = "Test" + _to_pascal_case(ec["id"] + " " + ec["condition"])
            lines.append(f"// {ec['id']}: {ec['condition']} -> {ec['behavior']}")
            lines.append(f"func {func_name}(t *testing.T) {{")
            lines.append(f"\t// Condition: {ec['condition']}")
            lines.append(f"\t// Expected: {ec['behavior']}")
            lines.append("")
            lines.append('\tt.Fatal("Not implemented")')
            lines.append("}")
            lines.append("")

        return "\n".join(lines)
GENERATORS = {
    "pytest": PytestGenerator,
    "jest": JestGenerator,
    "go-test": GoTestGenerator,
}
FILE_EXTENSIONS = {
    "pytest": ".py",
    "jest": ".test.ts",
    "go-test": "_test.go",
}
