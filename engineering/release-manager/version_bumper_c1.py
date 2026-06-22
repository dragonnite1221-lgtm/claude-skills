# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from version_bumper_base import *  # noqa: F403,E402
from version_bumper_p1 import Version  # noqa: F401,E501


class VersionBumperMixin1:
    def generate_bump_commands(self, new_version: Version) -> Dict[str, List[str]]:
        """Generate version bump commands for different package managers."""
        version_str = new_version.to_string()
        version_with_v = new_version.to_string(include_v_prefix=True)
        
        commands = {
            'npm': [
                f"npm version {version_str} --no-git-tag-version",
                f"# Or manually edit package.json version field to '{version_str}'"
            ],
            'python': [
                f"# Update version in setup.py, __init__.py, or pyproject.toml",
                f"# setup.py: version='{version_str}'",
                f"# pyproject.toml: version = '{version_str}'",
                f"# __init__.py: __version__ = '{version_str}'"
            ],
            'rust': [
                f"# Update Cargo.toml",
                f"# [package]",
                f"# version = '{version_str}'"
            ],
            'git': [
                f"git tag -a {version_with_v} -m 'Release {version_with_v}'",
                f"git push origin {version_with_v}"
            ],
            'docker': [
                f"docker build -t myapp:{version_str} .",
                f"docker tag myapp:{version_str} myapp:latest"
            ]
        }
        
        return commands
    def generate_file_updates(self, new_version: Version) -> Dict[str, str]:
        """Generate file update snippets for common package files."""
        version_str = new_version.to_string()
        
        updates = {}
        
        # package.json
        updates['package.json'] = json.dumps({
            "name": "your-package",
            "version": version_str,
            "description": "Your package description",
            "main": "index.js"
        }, indent=2)
        
        # pyproject.toml
        updates['pyproject.toml'] = f'''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package"
version = "{version_str}"
description = "Your package description"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
'''
        
        # setup.py  
        updates['setup.py'] = f'''from setuptools import setup, find_packages

setup(
    name="your-package",
    version="{version_str}",
    description="Your package description",
    packages=find_packages(),
    python_requires=">=3.8",
)
'''
        
        # Cargo.toml
        updates['Cargo.toml'] = f'''[package]
name = "your-package"
version = "{version_str}"
edition = "2021"
description = "Your package description"
'''
        
        # __init__.py
        updates['__init__.py'] = f'''"""Your package."""

__version__ = "{version_str}"
__author__ = "Your Name"
__email__ = "your.email@example.com"
'''
        
        return updates
