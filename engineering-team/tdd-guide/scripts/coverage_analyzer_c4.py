# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402
from coverage_analyzer_p0 import CoverageFormat  # noqa: F401,E501


class CoverageAnalyzerMixin4:
    def detect_format(self, content: str) -> str:
        """
        Automatically detect coverage report format.

        Args:
            content: Raw coverage report content

        Returns:
            Detected format (lcov, json, xml)
        """
        content_stripped = content.strip()

        # Check for LCOV format
        if content_stripped.startswith('TN:') or 'SF:' in content_stripped[:100]:
            return CoverageFormat.LCOV

        # Check for JSON format
        if content_stripped.startswith('{') or content_stripped.startswith('['):
            try:
                json.loads(content_stripped)
                return CoverageFormat.JSON
            except:
                pass

        # Check for XML format
        if content_stripped.startswith('<?xml') or content_stripped.startswith('<coverage'):
            return CoverageFormat.XML

        raise ValueError("Unable to detect coverage report format")
