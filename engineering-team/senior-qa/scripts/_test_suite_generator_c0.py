# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p0 import ComponentInfo, TestCase, TestFile  # noqa: F401,E501


class _TestGeneratorMixin0:
    """Generates Jest + React Testing Library test files"""
    def __init__(self, include_a11y: bool = False, template: Optional[str] = None):
        self.include_a11y = include_a11y
        self.template = template
    def generate(self, component: ComponentInfo) -> TestFile:
        """Generate a test file for a component"""
        test_file = TestFile(component=component)

        # Build imports
        test_file.imports.add("import { render, screen } from '@testing-library/react';")

        if component.has_callbacks:
            test_file.imports.add("import userEvent from '@testing-library/user-event';")

        if component.has_effects or component.has_state:
            test_file.imports.add("import { waitFor } from '@testing-library/react';")

        if self.include_a11y:
            test_file.imports.add("import { axe, toHaveNoViolations } from 'jest-axe';")

        # Add component import
        relative_path = self._get_relative_import(component.file_path)
        test_file.imports.add(f"import {{ {component.name} }} from '{relative_path}';")

        # Generate test cases
        test_file.test_cases.append(self._generate_render_test(component))

        if component.has_props:
            test_file.test_cases.append(self._generate_props_test(component))

        if component.has_callbacks:
            test_file.test_cases.append(self._generate_interaction_test(component))

        if component.has_state:
            test_file.test_cases.append(self._generate_state_test(component))

        if self.include_a11y:
            test_file.test_cases.append(self._generate_a11y_test(component))

        return test_file
    def _get_relative_import(self, file_path: str) -> str:
        """Get the relative import path for a component"""
        path = Path(file_path)
        # Remove extension
        stem = path.stem
        if stem == 'index':
            return f"../{path.parent.name}"
        return f"../{path.parent.name}/{stem}"
    def _generate_render_test(self, component: ComponentInfo) -> TestCase:
        """Generate a basic render test"""
        props_str = self._get_mock_props(component)

        code = f'''  it('renders without crashing', () => {{
    render(<{component.name}{props_str} />);
  }});

  it('renders expected content', () => {{
    render(<{component.name}{props_str} />);
    // TODO: Add specific content assertions
    // expect(screen.getByRole('...')).toBeInTheDocument();
  }});'''

        return TestCase(
            name='render',
            description='Basic render tests',
            test_type='render',
            code=code
        )
    def _generate_props_test(self, component: ComponentInfo) -> TestCase:
        """Generate props-related tests"""
        props = component.props[:3] if component.props else ['prop1']

        prop_tests = []
        for prop in props:
            prop_tests.append(f'''  it('renders with {prop} prop', () => {{
    render(<{component.name} {prop}="test-value" />);
    // TODO: Assert that {prop} affects rendering
  }});''')

        code = '\n\n'.join(prop_tests)

        return TestCase(
            name='props',
            description='Props handling tests',
            test_type='props',
            code=code
        )
