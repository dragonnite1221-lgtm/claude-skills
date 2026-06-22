# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from coverage_analyzer_base import *  # noqa: F403,E402


class CoverageAnalyzerMixin1:
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON format coverage report (Istanbul/nyc)."""
        try:
            data = json.loads(content)
            files = {}

            for file_path, file_data in data.items():
                lines = {}
                functions = {}
                branches = {}

                # Line coverage
                if 's' in file_data:  # Statement map
                    statement_map = file_data['s']
                    for stmt_id, hit_count in statement_map.items():
                        # Map statement to line number
                        if 'statementMap' in file_data:
                            stmt_info = file_data['statementMap'].get(stmt_id, {})
                            line_num = stmt_info.get('start', {}).get('line')
                            if line_num:
                                lines[line_num] = hit_count

                # Function coverage
                if 'f' in file_data:
                    func_map = file_data['f']
                    func_names = file_data.get('fnMap', {})
                    for func_id, hit_count in func_map.items():
                        func_info = func_names.get(func_id, {})
                        func_name = func_info.get('name', f'func_{func_id}')
                        functions[func_name] = hit_count

                # Branch coverage
                if 'b' in file_data:
                    branch_map = file_data['b']
                    for branch_id, locations in branch_map.items():
                        for idx, hit_count in enumerate(locations):
                            branch_key = f"{branch_id}:{idx}"
                            branches[branch_key] = hit_count

                files[file_path] = {
                    'lines': lines,
                    'functions': functions,
                    'branches': branches
                }

            self.coverage_data = files
            return files

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON coverage report: {e}")
    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """Parse XML/Cobertura format coverage report."""
        try:
            root = ET.fromstring(content)
            files = {}

            # Handle Cobertura format
            for package in root.findall('.//package'):
                for cls in package.findall('classes/class'):
                    filename = cls.get('filename', cls.get('name', 'unknown'))

                    lines = {}
                    branches = {}

                    for line in cls.findall('lines/line'):
                        line_num = int(line.get('number', 0))
                        hit_count = int(line.get('hits', 0))
                        lines[line_num] = hit_count

                        # Branch info
                        branch = line.get('branch', 'false')
                        if branch == 'true':
                            condition_coverage = line.get('condition-coverage', '0% (0/0)')
                            # Parse "(covered/total)"
                            if '(' in condition_coverage:
                                branch_info = condition_coverage.split('(')[1].split(')')[0]
                                covered, total = map(int, branch_info.split('/'))
                                branches[f"{line_num}:branch"] = covered

                    files[filename] = {
                        'lines': lines,
                        'functions': {},
                        'branches': branches
                    }

            self.coverage_data = files
            return files

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML coverage report: {e}")
