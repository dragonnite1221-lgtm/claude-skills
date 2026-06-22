# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dep_scanner_base import *  # noqa: F403,E402


class DependencyScannerMixin0:
    """Main dependency scanner class."""
    def __init__(self):
        self.known_vulnerabilities = self._load_vulnerability_database()
        self.supported_files = {
            'package.json': self._parse_package_json,
            'package-lock.json': self._parse_package_lock,
            'yarn.lock': self._parse_yarn_lock,
            'requirements.txt': self._parse_requirements_txt,
            'pyproject.toml': self._parse_pyproject_toml,
            'Pipfile.lock': self._parse_pipfile_lock,
            'poetry.lock': self._parse_poetry_lock,
            'go.mod': self._parse_go_mod,
            'go.sum': self._parse_go_sum,
            'Cargo.toml': self._parse_cargo_toml,
            'Cargo.lock': self._parse_cargo_lock,
            'Gemfile': self._parse_gemfile,
            'Gemfile.lock': self._parse_gemfile_lock,
        }
