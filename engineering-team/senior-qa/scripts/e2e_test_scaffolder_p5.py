# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402


class ConfigGenerator:
    """Generates Playwright configuration"""

    def generate_config(self) -> str:
        """Generate playwright.config.ts"""
        return '''import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Test Configuration
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
'''

    def generate_auth_fixture(self) -> str:
        """Generate authentication fixture"""
        return '''import { test as base, Page } from '@playwright/test';

interface AuthFixtures {
  authenticatedPage: Page;
}

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Option 1: Login via UI
    // await page.goto('/login');
    // await page.getByLabel('Email').fill(process.env.TEST_EMAIL || 'test@example.com');
    // await page.getByLabel('Password').fill(process.env.TEST_PASSWORD || 'password');
    // await page.getByRole('button', { name: 'Sign in' }).click();
    // await page.waitForURL('/dashboard');

    // Option 2: Login via API
    // const response = await page.request.post('/api/auth/login', {
    //   data: {
    //     email: process.env.TEST_EMAIL,
    //     password: process.env.TEST_PASSWORD,
    //   },
    // });
    // const { token } = await response.json();
    // await page.context().addCookies([
    //   { name: 'auth-token', value: token, domain: 'localhost', path: '/' }
    // ]);

    await use(page);
  },
});

export { expect } from '@playwright/test';
'''
