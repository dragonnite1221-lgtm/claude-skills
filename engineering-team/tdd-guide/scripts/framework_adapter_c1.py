# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from framework_adapter_base import *  # noqa: F403,E402
from framework_adapter_p0 import Framework  # noqa: F401,E501


class FrameworkAdapterMixin1:
    def generate_test_function(
        self,
        test_name: str,
        test_body: str,
        description: str = ""
    ) -> str:
        """
        Generate framework-specific test function.

        Args:
            test_name: Name of test
            test_body: Test body code
            description: Test description

        Returns:
            Complete test function
        """
        if self.framework == Framework.JEST:
            return self._jest_test(test_name, test_body, description)
        elif self.framework == Framework.VITEST:
            return self._vitest_test(test_name, test_body, description)
        elif self.framework == Framework.PYTEST:
            return self._pytest_test(test_name, test_body, description)
        elif self.framework == Framework.UNITTEST:
            return self._unittest_test(test_name, test_body, description)
        elif self.framework == Framework.JUNIT:
            return self._junit_test(test_name, test_body, description)
        elif self.framework == Framework.TESTNG:
            return self._testng_test(test_name, test_body, description)
        elif self.framework == Framework.MOCHA:
            return self._mocha_test(test_name, test_body, description)
        else:
            return ""
    def _jest_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate Jest test."""
        return f"""it('{test_name}', () => {{
  // {description}
{self._indent(test_body, 2)}
}});"""
    def _vitest_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate Vitest test."""
        return f"""it('{test_name}', () => {{
  // {description}
{self._indent(test_body, 2)}
}});"""
    def _pytest_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate Pytest test."""
        func_name = test_name.replace(' ', '_').replace('-', '_')
        return f"""def test_{func_name}(self):
    \"\"\"
    {description or test_name}
    \"\"\"
{self._indent(test_body, 4)}"""
    def _unittest_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate unittest test."""
        func_name = self._to_camel_case(test_name)
        return f"""def test_{func_name}(self):
    \"\"\"
    {description or test_name}
    \"\"\"
{self._indent(test_body, 4)}"""
    def _junit_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate JUnit test."""
        method_name = self._to_camel_case(test_name)
        return f"""@Test
public void test{method_name}() {{
    // {description}
{self._indent(test_body, 4)}
}}"""
    def _testng_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate TestNG test."""
        method_name = self._to_camel_case(test_name)
        return f"""@Test
public void test{method_name}() {{
    // {description}
{self._indent(test_body, 4)}
}}"""
    def _mocha_test(self, test_name: str, test_body: str, description: str) -> str:
        """Generate Mocha test."""
        return f"""it('{test_name}', () => {{
  // {description}
{self._indent(test_body, 2)}
}});"""
    def generate_assertion(
        self,
        actual: str,
        expected: str,
        assertion_type: str = "equals"
    ) -> str:
        """
        Generate framework-specific assertion.

        Args:
            actual: Actual value expression
            expected: Expected value expression
            assertion_type: Type of assertion (equals, not_equals, true, false, throws)

        Returns:
            Assertion statement
        """
        if self.framework in [Framework.JEST, Framework.VITEST]:
            return self._jest_assertion(actual, expected, assertion_type)
        elif self.framework in [Framework.PYTEST, Framework.UNITTEST]:
            return self._python_assertion(actual, expected, assertion_type)
        elif self.framework in [Framework.JUNIT, Framework.TESTNG]:
            return self._java_assertion(actual, expected, assertion_type)
        elif self.framework == Framework.MOCHA:
            return self._chai_assertion(actual, expected, assertion_type)
        else:
            return f"assert {actual} == {expected}"
