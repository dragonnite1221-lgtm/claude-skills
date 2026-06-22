# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402
from coverage_analyzer_p0 import CoverageFormat  # noqa: F401,E501


class CoverageAnalyzerMixin0:
    """Analyze test coverage reports and identify gaps."""
    def __init__(self):
        """Initialize coverage analyzer."""
        self.coverage_data = {}
        self.gaps = []
        self.summary = {}
    def parse_coverage_report(
        self,
        report_content: str,
        format_type: str
    ) -> Dict[str, Any]:
        """
        Parse coverage report in various formats.

        Args:
            report_content: Raw coverage report content
            format_type: Format (lcov, json, xml, cobertura)

        Returns:
            Parsed coverage data
        """
        if format_type == CoverageFormat.LCOV:
            return self._parse_lcov(report_content)
        elif format_type == CoverageFormat.JSON:
            return self._parse_json(report_content)
        elif format_type in [CoverageFormat.XML, CoverageFormat.COBERTURA]:
            return self._parse_xml(report_content)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    def _parse_lcov(self, content: str) -> Dict[str, Any]:
        """Parse LCOV format coverage report."""
        files = {}
        current_file = None
        file_data = {}

        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('SF:'):
                # Source file
                current_file = line[3:]
                file_data = {
                    'lines': {},
                    'functions': {},
                    'branches': {}
                }

            elif line.startswith('DA:'):
                # Line coverage data (line_number,hit_count)
                parts = line[3:].split(',')
                line_num = int(parts[0])
                hit_count = int(parts[1])
                file_data['lines'][line_num] = hit_count

            elif line.startswith('FNDA:'):
                # Function coverage (hit_count,function_name)
                parts = line[5:].split(',', 1)
                hit_count = int(parts[0])
                func_name = parts[1] if len(parts) > 1 else 'unknown'
                file_data['functions'][func_name] = hit_count

            elif line.startswith('BRDA:'):
                # Branch coverage (line,block,branch,hit_count)
                parts = line[5:].split(',')
                branch_id = f"{parts[0]}:{parts[1]}:{parts[2]}"
                hit_count = 0 if parts[3] == '-' else int(parts[3])
                file_data['branches'][branch_id] = hit_count

            elif line == 'end_of_record':
                if current_file:
                    files[current_file] = file_data
                current_file = None
                file_data = {}

        self.coverage_data = files
        return files
