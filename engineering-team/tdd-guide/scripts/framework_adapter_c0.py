# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from framework_adapter_base import *  # noqa: F403,E402
from framework_adapter_p0 import Framework, Language  # noqa: F401,E501


class FrameworkAdapterMixin0:
    """Adapter for multiple testing frameworks."""
    def __init__(self, framework: Framework, language: Language):
        """
        Initialize framework adapter.

        Args:
            framework: Testing framework
            language: Programming language
        """
        self.framework = framework
        self.language = language
    def generate_imports(self) -> str:
        """Generate framework-specific imports."""
        if self.framework == Framework.JEST:
            return self._jest_imports()
        elif self.framework == Framework.VITEST:
            return self._vitest_imports()
        elif self.framework == Framework.PYTEST:
            return self._pytest_imports()
        elif self.framework == Framework.UNITTEST:
            return self._unittest_imports()
        elif self.framework == Framework.JUNIT:
            return self._junit_imports()
        elif self.framework == Framework.TESTNG:
            return self._testng_imports()
        elif self.framework == Framework.MOCHA:
            return self._mocha_imports()
        else:
            return ""
    def _jest_imports(self) -> str:
        """Generate Jest imports."""
        return """import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';"""
    def _vitest_imports(self) -> str:
        """Generate Vitest imports."""
        return """import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';"""
    def _pytest_imports(self) -> str:
        """Generate Pytest imports."""
        return """import pytest"""
    def _unittest_imports(self) -> str:
        """Generate unittest imports."""
        return """import unittest"""
    def _junit_imports(self) -> str:
        """Generate JUnit imports."""
        return """import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;"""
    def _testng_imports(self) -> str:
        """Generate TestNG imports."""
        return """import org.testng.annotations.Test;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.AfterMethod;
import static org.testng.Assert.*;"""
    def _mocha_imports(self) -> str:
        """Generate Mocha imports."""
        return """import { describe, it, beforeEach, afterEach } from 'mocha';
import { expect } from 'chai';"""
    def generate_test_suite_wrapper(
        self,
        suite_name: str,
        test_content: str
    ) -> str:
        """
        Wrap test content in framework-specific suite structure.

        Args:
            suite_name: Name of test suite
            test_content: Test functions/methods

        Returns:
            Complete test suite code
        """
        if self.framework in [Framework.JEST, Framework.VITEST, Framework.MOCHA]:
            return f"""describe('{suite_name}', () => {{
{self._indent(test_content, 2)}
}});"""

        elif self.framework == Framework.PYTEST:
            return f"""class Test{self._to_class_name(suite_name)}:
    \"\"\"Test suite for {suite_name}.\"\"\"

{self._indent(test_content, 4)}"""

        elif self.framework == Framework.UNITTEST:
            return f"""class Test{self._to_class_name(suite_name)}(unittest.TestCase):
    \"\"\"Test suite for {suite_name}.\"\"\"

{self._indent(test_content, 4)}"""

        elif self.framework in [Framework.JUNIT, Framework.TESTNG]:
            return f"""public class {self._to_class_name(suite_name)}Test {{

{self._indent(test_content, 4)}
}}"""

        return test_content
