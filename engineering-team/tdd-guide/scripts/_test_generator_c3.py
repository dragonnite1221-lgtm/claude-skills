# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_generator_base import *  # noqa: F403,E402


class _TestGeneratorMixin3:
    def _generate_junit_file(self, module_name: str, test_cases: List[Dict[str, Any]]) -> str:
        """Generate complete JUnit test file."""
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))

        imports = """import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

"""

        class_header = f"public class {class_name}Test {{\n\n"

        stubs = []
        for test_case in test_cases:
            stubs.append(self._generate_junit_stub(test_case))

        class_footer = "\n}"

        return imports + class_header + "\n\n".join(stubs) + class_footer
    def _generate_vitest_file(self, module_name: str, test_cases: List[Dict[str, Any]]) -> str:
        """Generate complete Vitest test file."""
        imports = f"import {{ describe, it, expect }} from 'vitest';\nimport {{ {module_name} }} from '../{module_name}';\n\n"

        stubs = []
        for test_case in test_cases:
            stubs.append(self._generate_vitest_stub(test_case))

        return imports + "\n\n".join(stubs)
    def suggest_missing_scenarios(
        self,
        existing_tests: List[str],
        code_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest missing test scenarios based on code analysis.

        Args:
            existing_tests: List of existing test names
            code_analysis: Analysis of code under test (branches, error paths, etc.)

        Returns:
            List of suggested test scenarios
        """
        suggestions = []

        # Check for untested error conditions
        if 'error_handlers' in code_analysis:
            for error_handler in code_analysis['error_handlers']:
                error_name = error_handler.get('type', 'error')
                if not self._has_test_for(existing_tests, error_name):
                    suggestions.append({
                        'name': f"should_handle_{error_name}",
                        'type': 'error_case',
                        'reason': 'Error handler exists but no corresponding test',
                        'priority': 'P0'
                    })

        # Check for untested branches
        if 'conditional_branches' in code_analysis:
            for branch in code_analysis['conditional_branches']:
                branch_name = branch.get('condition', 'condition')
                if not self._has_test_for(existing_tests, branch_name):
                    suggestions.append({
                        'name': f"should_test_{branch_name}_branch",
                        'type': 'branch_coverage',
                        'reason': 'Conditional branch not fully tested',
                        'priority': 'P1'
                    })

        # Check for boundary conditions
        if 'input_validation' in code_analysis:
            for validation in code_analysis['input_validation']:
                param = validation.get('parameter', 'input')
                if not self._has_test_for(existing_tests, f"{param}_boundary"):
                    suggestions.append({
                        'name': f"should_test_{param}_boundary_values",
                        'type': 'boundary',
                        'reason': 'Input validation exists but boundary tests missing',
                        'priority': 'P1'
                    })

        return suggestions
    def _has_test_for(self, existing_tests: List[str], keyword: str) -> bool:
        """Check if existing tests cover a keyword/scenario."""
        keyword_lower = keyword.lower().replace('_', '').replace('-', '')
        for test in existing_tests:
            test_lower = test.lower().replace('_', '').replace('-', '')
            if keyword_lower in test_lower:
                return True
        return False
