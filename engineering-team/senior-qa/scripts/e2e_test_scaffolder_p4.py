# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from e2e_test_scaffolder_p1 import RouteInfo  # noqa: E402,E501
# fmt: on


class PageObjectGenerator:
    """Generates Page Object Model classes"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def generate(self, route: RouteInfo) -> str:
        """Generate a Page Object class for a route"""
        class_name = self._get_class_name(route.path)
        url = route.path

        # Replace dynamic segments
        for param in route.params:
            url = url.replace(f'[{param}]', f'${{{param}}}')

        lines = []

        # Imports
        lines.append("import { Page, Locator, expect } from '@playwright/test';")
        lines.append('')

        # Class definition
        lines.append(f"export class {class_name} {{")
        lines.append("  readonly page: Page;")

        # Common locators
        locators = self._get_locators(route)
        for name, selector, _ in locators:
            lines.append(f"  readonly {name}: Locator;")

        lines.append('')

        # Constructor
        lines.append("  constructor(page: Page) {")
        lines.append("    this.page = page;")
        for name, selector, _ in locators:
            lines.append(f"    this.{name} = page.{selector};")
        lines.append("  }")
        lines.append('')

        # Navigation method
        if route.has_params:
            param_args = ', '.join(f'{p}: string' for p in route.params)
            url_parts = url.split('/')
            url_template = '/'.join(
                f'${{{p}}}' if f'${{{p}}}' in part else part
                for p, part in zip(route.params, url_parts)
            )
            lines.append(f"  async goto({param_args}) {{")
            lines.append(f"    await this.page.goto(`{url_template}`);")
        else:
            lines.append("  async goto() {")
            lines.append(f"    await this.page.goto('{route.path}');")
        lines.append("  }")
        lines.append('')

        # Add methods based on features
        methods = self._get_methods(route, locators)
        for method_name, method_code in methods:
            lines.append(method_code)
            lines.append('')

        lines.append('}')
        lines.append('')

        return '\n'.join(lines)

    def _get_class_name(self, route_path: str) -> str:
        """Get class name from route path"""
        if route_path == '/':
            return 'HomePage'

        name = route_path.strip('/')
        name = re.sub(r'\[.*?\]', '', name)
        parts = name.split('/')
        return ''.join(p.title() for p in parts if p) + 'Page'

    def _get_locators(self, route: RouteInfo) -> List[Tuple[str, str, str]]:
        """Get common locators for a page"""
        locators = []

        # Always add a heading locator
        locators.append(('heading', "getByRole('heading', { level: 1 })", 'Main heading'))

        if route.has_form:
            locators.extend([
                ('submitButton', "getByRole('button', { name: /submit/i })", 'Form submit button'),
                ('form', "locator('form')", 'Main form element'),
            ])

        if route.has_auth:
            locators.extend([
                ('emailInput', "getByLabel('Email')", 'Email input field'),
                ('passwordInput', "getByLabel('Password')", 'Password input field'),
            ])

        if 'navigation' in route.interactions:
            locators.append(('navLinks', "getByRole('navigation').getByRole('link')", 'Navigation links'))

        if 'modal' in route.interactions:
            locators.append(('modal', "getByRole('dialog')", 'Modal dialog'))

        return locators

    def _get_methods(
        self,
        route: RouteInfo,
        locators: List[Tuple[str, str, str]]
    ) -> List[Tuple[str, str]]:
        """Get methods for the page object"""
        methods = []

        # Wait for load method
        methods.append(('waitForLoad', '''  async waitForLoad() {
    await expect(this.heading).toBeVisible();
  }'''))

        if route.has_form:
            methods.append(('submitForm', '''  async submitForm() {
    await this.submitButton.click();
  }'''))

        if route.has_auth:
            methods.append(('login', '''  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }'''))

        if 'modal' in route.interactions:
            methods.append(('waitForModal', '''  async waitForModal() {
    await expect(this.modal).toBeVisible();
  }'''))
            methods.append(('closeModal', '''  async closeModal() {
    await this.page.keyboard.press('Escape');
    await expect(this.modal).not.toBeVisible();
  }'''))

        return methods
