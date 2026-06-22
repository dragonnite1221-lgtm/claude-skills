# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from e2e_test_scaffolder_p1 import RouteInfo  # noqa: E402,E501
# fmt: on


class TestGenerator:
    """Generates Playwright test files"""

    def __init__(self, include_pom: bool = False, verbose: bool = False):
        self.include_pom = include_pom
        self.verbose = verbose

    def generate(self, route: RouteInfo) -> str:
        """Generate a test file for a route"""
        lines = []

        # Imports
        lines.append("import { test, expect } from '@playwright/test';")

        if self.include_pom:
            page_class = self._get_page_class_name(route.path)
            lines.append(f"import {{ {page_class} }} from './pages/{page_class}';")

        lines.append('')

        # Test describe block
        route_name = route.path if route.path != '/' else 'Home'
        lines.append(f"test.describe('{route_name}', () => {{")

        # Generate test cases based on route features
        test_cases = self._generate_test_cases(route)

        for test_case in test_cases:
            lines.append('')
            lines.append(test_case)

        lines.append('});')
        lines.append('')

        return '\n'.join(lines)

    def _generate_test_cases(self, route: RouteInfo) -> List[str]:
        """Generate test cases based on route features"""
        cases = []
        url = self._get_test_url(route)

        # Basic navigation test
        cases.append(f'''  test('loads successfully', async ({{ page }}) => {{
    await page.goto('{url}');
    await expect(page).toHaveURL(/{re.escape(route.path.replace('[', '').replace(']', '.*'))}/);
    // TODO: Add specific content assertions
  }});''')

        # Page title test
        cases.append(f'''  test('has correct title', async ({{ page }}) => {{
    await page.goto('{url}');
    // TODO: Update expected title
    await expect(page).toHaveTitle(/.*/);
  }});''')

        # Auth-related tests
        if route.has_auth:
            cases.append(f'''  test('redirects unauthenticated users', async ({{ page }}) => {{
    await page.goto('{url}');
    // TODO: Verify redirect to login
    // await expect(page).toHaveURL('/login');
  }});

  test('allows authenticated access', async ({{ page }}) => {{
    // TODO: Set up authentication
    // await page.context().addCookies([{{ name: 'session', value: '...' }}]);
    await page.goto('{url}');
    await expect(page).toHaveURL(/{re.escape(route.path.replace('[', '').replace(']', '.*'))}/);
  }});''')

        # Form tests
        if route.has_form:
            cases.append(f'''  test('form submission works', async ({{ page }}) => {{
    await page.goto('{url}');

    // TODO: Fill in form fields
    // await page.getByLabel('Email').fill('test@example.com');
    // await page.getByLabel('Password').fill('password123');

    // Submit form
    // await page.getByRole('button', {{ name: 'Submit' }}).click();

    // TODO: Assert success state
    // await expect(page.getByText('Success')).toBeVisible();
  }});

  test('shows validation errors', async ({{ page }}) => {{
    await page.goto('{url}');

    // Submit without filling required fields
    await page.getByRole('button', {{ name: /submit/i }}).click();

    // TODO: Assert validation errors shown
    // await expect(page.getByText('Required')).toBeVisible();
  }});''')

        # Click interaction tests
        if 'click' in route.interactions:
            cases.append(f'''  test('button interactions work', async ({{ page }}) => {{
    await page.goto('{url}');

    // TODO: Find and click interactive elements
    // const button = page.getByRole('button', {{ name: '...' }});
    // await button.click();
    // await expect(page.getByText('...')).toBeVisible();
  }});''')

        # Navigation tests
        if 'navigation' in route.interactions:
            cases.append(f'''  test('navigation works correctly', async ({{ page }}) => {{
    await page.goto('{url}');

    // TODO: Click navigation links
    // await page.getByRole('link', {{ name: '...' }}).click();
    // await expect(page).toHaveURL('...');
  }});''')

        # Modal tests
        if 'modal' in route.interactions:
            cases.append(f'''  test('modal opens and closes', async ({{ page }}) => {{
    await page.goto('{url}');

    // TODO: Open modal
    // await page.getByRole('button', {{ name: 'Open' }}).click();
    // await expect(page.getByRole('dialog')).toBeVisible();

    // TODO: Close modal
    // await page.getByRole('button', {{ name: 'Close' }}).click();
    // await expect(page.getByRole('dialog')).not.toBeVisible();
  }});''')

        # Dynamic route test
        if route.has_params:
            cases.append(f'''  test('handles dynamic parameters', async ({{ page }}) => {{
    // TODO: Test with different parameter values
    await page.goto('{url}');
    await expect(page.locator('body')).toBeVisible();
  }});''')

        return cases

    def _get_test_url(self, route: RouteInfo) -> str:
        """Get a testable URL for the route"""
        url = route.path

        # Replace dynamic segments with example values
        for param in route.params:
            if param.startswith('...'):
                url = url.replace(f'[...{param[3:]}]', 'example/path')
            else:
                url = url.replace(f'[{param}]', 'test-id')

        return url

    def _get_page_class_name(self, route_path: str) -> str:
        """Get Page Object class name from route path"""
        if route_path == '/':
            return 'HomePage'

        # Remove leading slash and convert to PascalCase
        name = route_path.strip('/')
        name = re.sub(r'\[.*?\]', '', name)  # Remove dynamic segments
        parts = name.split('/')
        return ''.join(p.title() for p in parts if p) + 'Page'
