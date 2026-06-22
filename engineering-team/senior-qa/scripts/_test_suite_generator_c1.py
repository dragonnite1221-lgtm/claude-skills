# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p0 import ComponentInfo, TestCase  # noqa: F401,E501


class _TestGeneratorMixin1:
    def _generate_interaction_test(self, component: ComponentInfo) -> TestCase:
        """Generate user interaction tests"""
        code = f'''  it('handles user interaction', async () => {{
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(<{component.name} onClick={{handleClick}} />);

    // TODO: Find the interactive element
    const button = screen.getByRole('button');
    await user.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  }});

  it('handles keyboard navigation', async () => {{
    const user = userEvent.setup();
    render(<{component.name} />);

    // TODO: Add keyboard interaction tests
    // await user.tab();
    // expect(screen.getByRole('...')).toHaveFocus();
  }});'''

        return TestCase(
            name='interaction',
            description='User interaction tests',
            test_type='interaction',
            code=code
        )
    def _generate_state_test(self, component: ComponentInfo) -> TestCase:
        """Generate state-related tests"""
        code = f'''  it('updates state correctly', async () => {{
    const user = userEvent.setup();
    render(<{component.name} />);

    // TODO: Trigger state change
    // await user.click(screen.getByRole('button'));

    // TODO: Assert state change is reflected in UI
    await waitFor(() => {{
      // expect(screen.getByText('...')).toBeInTheDocument();
    }});
  }});'''

        return TestCase(
            name='state',
            description='State management tests',
            test_type='state',
            code=code
        )
    def _generate_a11y_test(self, component: ComponentInfo) -> TestCase:
        """Generate accessibility test"""
        props_str = self._get_mock_props(component)

        code = f'''  it('has no accessibility violations', async () => {{
    const {{ container }} = render(<{component.name}{props_str} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  }});'''

        return TestCase(
            name='accessibility',
            description='Accessibility tests',
            test_type='a11y',
            code=code
        )
    def _get_mock_props(self, component: ComponentInfo) -> str:
        """Generate mock props string for a component"""
        if not component.has_props or not component.props:
            return ''

        # Return empty for simplicity, user should fill in
        return ' {...mockProps}'
