# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p0 import TestFile  # noqa: F401,E501


class _TestGeneratorMixin2:
    def format_test_file(self, test_file: TestFile) -> str:
        """Format the complete test file content"""
        lines = []

        # Imports
        lines.append("import '@testing-library/jest-dom';")
        for imp in sorted(test_file.imports):
            lines.append(imp)

        lines.append('')

        # A11y setup if needed
        if self.include_a11y:
            lines.append('expect.extend(toHaveNoViolations);')
            lines.append('')

        # Mock props if component has props
        if test_file.component.has_props:
            lines.append('// TODO: Define mock props')
            lines.append('const mockProps = {};')
            lines.append('')

        # Describe block
        lines.append(f"describe('{test_file.component.name}', () => {{")

        # Test cases grouped by type
        test_types = {}
        for test_case in test_file.test_cases:
            if test_case.test_type not in test_types:
                test_types[test_case.test_type] = []
            test_types[test_case.test_type].append(test_case)

        for test_type, cases in test_types.items():
            for case in cases:
                lines.append('')
                lines.append(f'  // {case.description}')
                lines.append(case.code)

        lines.append('});')
        lines.append('')

        return '\n'.join(lines)
