# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from framework_adapter_base import *  # noqa: F403,E402
from framework_adapter_p0 import Framework  # noqa: F401,E501


class FrameworkAdapterMixin3:
    def _indent(self, text: str, spaces: int) -> str:
        """Indent text by number of spaces."""
        indent = " " * spaces
        lines = text.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = text.replace('-', ' ').replace('_', ' ').split()
        if not words:
            return text
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    def _to_class_name(self, text: str) -> str:
        """Convert text to ClassName."""
        words = text.replace('-', ' ').replace('_', ' ').split()
        return ''.join(word.capitalize() for word in words)
    def detect_framework(self, code: str) -> Optional[Framework]:
        """
        Auto-detect testing framework from code.

        Args:
            code: Test code

        Returns:
            Detected framework or None
        """
        # Jest patterns
        if 'from \'@jest/globals\'' in code or '@jest/' in code:
            return Framework.JEST

        # Vitest patterns
        if 'from \'vitest\'' in code or 'import { vi }' in code:
            return Framework.VITEST

        # Pytest patterns
        if 'import pytest' in code or 'def test_' in code and 'pytest.fixture' in code:
            return Framework.PYTEST

        # Unittest patterns
        if 'import unittest' in code and 'unittest.TestCase' in code:
            return Framework.UNITTEST

        # JUnit patterns
        if '@Test' in code and 'import org.junit' in code:
            return Framework.JUNIT

        # TestNG patterns
        if '@Test' in code and 'import org.testng' in code:
            return Framework.TESTNG

        # Mocha patterns
        if 'from \'mocha\'' in code or ('describe(' in code and 'from \'chai\'' in code):
            return Framework.MOCHA

        return None
