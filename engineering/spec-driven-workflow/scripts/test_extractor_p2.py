# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_extractor_base import *  # noqa: F403,E402
# fmt: off
from test_extractor_p1 import _sanitize_name  # noqa: E402,E501
# fmt: on


def _to_pascal_case(name: str) -> str:
    """Convert to PascalCase for Go test names."""
    parts = _sanitize_name(name).split("_")
    return "".join(p.capitalize() for p in parts if p)
class PytestGenerator:
    """Generates pytest test stubs."""

    def generate(self, title: str, criteria: List[Dict], edge_cases: List[Dict]) -> str:
        class_name = "Test" + _to_pascal_case(title)
        lines = [
            '"""',
            f"Test suite for: {title}",
            f"Auto-generated from spec. {len(criteria)} acceptance criteria, {len(edge_cases)} edge cases.",
            "",
            "All tests are stubs — implement the test body to make them pass.",
            '"""',
            "",
            "import pytest",
            "",
            "",
            f"class {class_name}:",
            f'    """Tests for {title}."""',
            "",
        ]

        for ac in criteria:
            method_name = f"test_{ac['id'].lower().replace('-', '')}_{_sanitize_name(ac['name'])}"
            docstring = f'{ac["id"]}: {ac["name"]}'
            ref_str = f" [{', '.join(ac['references'])}]" if ac["references"] else ""

            lines.append(f"    def {method_name}(self):")
            lines.append(f'        """{docstring}{ref_str}"""')

            if ac["given"]:
                lines.append(f"        # Given {ac['given']}")
            if ac["when"]:
                lines.append(f"        # When {ac['when']}")
            for t in ac["then"]:
                lines.append(f"        # Then {t}")

            lines.append('        raise NotImplementedError("Implement this test")')
            lines.append("")

        if edge_cases:
            lines.append("    # --- Edge Cases ---")
            lines.append("")

        for ec in edge_cases:
            method_name = f"test_{ec['id'].lower().replace('-', '')}_{_sanitize_name(ec['condition'])}"
            lines.append(f"    def {method_name}(self):")
            lines.append(f'        """{ec["id"]}: {ec["condition"]} -> {ec["behavior"]}"""')
            lines.append(f"        # Condition: {ec['condition']}")
            lines.append(f"        # Expected: {ec['behavior']}")
            lines.append('        raise NotImplementedError("Implement this test")')
            lines.append("")

        return "\n".join(lines)
class JestGenerator:
    """Generates Jest/Vitest test stubs (TypeScript)."""

    def generate(self, title: str, criteria: List[Dict], edge_cases: List[Dict]) -> str:
        lines = [
            f"/**",
            f" * Test suite for: {title}",
            f" * Auto-generated from spec. {len(criteria)} acceptance criteria, {len(edge_cases)} edge cases.",
            f" *",
            f" * All tests are stubs — implement the test body to make them pass.",
            f" */",
            "",
            f'describe("{title}", () => {{',
        ]

        for ac in criteria:
            ref_str = f" [{', '.join(ac['references'])}]" if ac["references"] else ""
            test_name = f"{ac['id']}: {ac['name']}{ref_str}"

            lines.append(f'  it("{test_name}", () => {{')
            if ac["given"]:
                lines.append(f"    // Given {ac['given']}")
            if ac["when"]:
                lines.append(f"    // When {ac['when']}")
            for t in ac["then"]:
                lines.append(f"    // Then {t}")
            lines.append("")
            lines.append('    throw new Error("Not implemented");')
            lines.append("  });")
            lines.append("")

        if edge_cases:
            lines.append("  // --- Edge Cases ---")
            lines.append("")

        for ec in edge_cases:
            test_name = f"{ec['id']}: {ec['condition']}"
            lines.append(f'  it("{test_name}", () => {{')
            lines.append(f"    // Condition: {ec['condition']}")
            lines.append(f"    // Expected: {ec['behavior']}")
            lines.append("")
            lines.append('    throw new Error("Not implemented");')
            lines.append("  });")
            lines.append("")

        lines.append("});")
        lines.append("")

        return "\n".join(lines)
