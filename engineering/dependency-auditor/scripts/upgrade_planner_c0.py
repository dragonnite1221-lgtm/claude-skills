# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from upgrade_planner_base import *  # noqa: F403,E402


class UpgradePlannerMixin0:
    """Main upgrade planning and risk analysis class."""
    def __init__(self):
        self.breaking_change_patterns = self._build_breaking_change_patterns()
        self.ecosystem_knowledge = self._build_ecosystem_knowledge()
        self.security_advisories = self._build_security_advisories()
    def _build_breaking_change_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for detecting breaking changes."""
        return {
            'npm': [
                r'BREAKING\s*CHANGE',
                r'breaking\s*change',
                r'major\s*version',
                r'removed.*API',
                r'deprecated.*removed',
                r'no\s*longer\s*supported',
                r'minimum.*node.*version',
                r'peer.*dependency.*change'
            ],
            'pypi': [
                r'BREAKING\s*CHANGE',
                r'breaking\s*change',
                r'removed.*function',
                r'deprecated.*removed',
                r'minimum.*python.*version',
                r'incompatible.*change',
                r'API.*change'
            ],
            'maven': [
                r'BREAKING\s*CHANGE',
                r'breaking\s*change',
                r'removed.*method',
                r'deprecated.*removed',
                r'minimum.*java.*version',
                r'API.*incompatible'
            ]
        }
    def _build_ecosystem_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Build ecosystem-specific upgrade knowledge."""
        return {
            'npm': {
                'typical_major_cycle_months': 12,
                'typical_patch_cycle_weeks': 2,
                'deprecation_notice_months': 6,
                'lts_support_years': 3,
                'common_breaking_changes': [
                    'Node.js version requirements',
                    'Peer dependency updates',
                    'API signature changes',
                    'Configuration format changes'
                ]
            },
            'pypi': {
                'typical_major_cycle_months': 18,
                'typical_patch_cycle_weeks': 4,
                'deprecation_notice_months': 12,
                'lts_support_years': 2,
                'common_breaking_changes': [
                    'Python version requirements',
                    'Function signature changes',
                    'Import path changes',
                    'Configuration changes'
                ]
            },
            'maven': {
                'typical_major_cycle_months': 24,
                'typical_patch_cycle_weeks': 6,
                'deprecation_notice_months': 12,
                'lts_support_years': 5,
                'common_breaking_changes': [
                    'Java version requirements',
                    'Method signature changes',
                    'Package restructuring',
                    'Dependency changes'
                ]
            },
            'cargo': {
                'typical_major_cycle_months': 6,
                'typical_patch_cycle_weeks': 2,
                'deprecation_notice_months': 3,
                'lts_support_years': 1,
                'common_breaking_changes': [
                    'Rust edition changes',
                    'Trait changes',
                    'Module restructuring',
                    'Macro changes'
                ]
            }
        }
