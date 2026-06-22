# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import LicenseInfo  # noqa: F401,E501
from license_checker_p1 import _mod_cg0_0  # noqa: F401,E501
from license_checker_p2 import _mod_cg0_1  # noqa: F401,E501


class LicenseCheckerMixin0:
    """Main license checking and compliance analysis class."""
    def __init__(self):
        self.license_database = self._build_license_database()
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.license_patterns = self._build_license_patterns()
    def _build_license_database(self) -> Dict[str, LicenseInfo]:
        """Build comprehensive license database with risk classifications."""
        return {**_mod_cg0_0(), **_mod_cg0_1()}
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, bool]]:
        """Build license compatibility matrix."""
        return {
            'MIT': {
                'MIT': True, 'Apache-2.0': True, 'BSD-3-Clause': True, 'BSD-2-Clause': True,
                'ISC': True, 'MPL-2.0': True, 'LGPL-2.1': True, 'LGPL-3.0': True,
                'GPL-2.0': False, 'GPL-3.0': False, 'AGPL-3.0': False, 'PROPRIETARY': False
            },
            'Apache-2.0': {
                'MIT': True, 'Apache-2.0': True, 'BSD-3-Clause': True, 'BSD-2-Clause': True,
                'ISC': True, 'MPL-2.0': True, 'LGPL-2.1': False, 'LGPL-3.0': True,
                'GPL-2.0': False, 'GPL-3.0': True, 'AGPL-3.0': True, 'PROPRIETARY': False
            },
            'GPL-2.0': {
                'MIT': True, 'Apache-2.0': False, 'BSD-3-Clause': True, 'BSD-2-Clause': True,
                'ISC': True, 'MPL-2.0': False, 'LGPL-2.1': True, 'LGPL-3.0': False,
                'GPL-2.0': True, 'GPL-3.0': False, 'AGPL-3.0': False, 'PROPRIETARY': False
            },
            'GPL-3.0': {
                'MIT': True, 'Apache-2.0': True, 'BSD-3-Clause': True, 'BSD-2-Clause': True,
                'ISC': True, 'MPL-2.0': True, 'LGPL-2.1': False, 'LGPL-3.0': True,
                'GPL-2.0': False, 'GPL-3.0': True, 'AGPL-3.0': True, 'PROPRIETARY': False
            },
            'AGPL-3.0': {
                'MIT': True, 'Apache-2.0': True, 'BSD-3-Clause': True, 'BSD-2-Clause': True,
                'ISC': True, 'MPL-2.0': True, 'LGPL-2.1': False, 'LGPL-3.0': True,
                'GPL-2.0': False, 'GPL-3.0': True, 'AGPL-3.0': True, 'PROPRIETARY': False
            }
        }
    def _build_license_patterns(self) -> Dict[str, List[str]]:
        """Build license detection patterns for text analysis."""
        return {
            'MIT': [
                r'MIT License',
                r'Permission is hereby granted, free of charge',
                r'THE SOFTWARE IS PROVIDED "AS IS"'
            ],
            'Apache-2.0': [
                r'Apache License, Version 2\.0',
                r'Licensed under the Apache License',
                r'http://www\.apache\.org/licenses/LICENSE-2\.0'
            ],
            'GPL-2.0': [
                r'GNU GENERAL PUBLIC LICENSE\s+Version 2',
                r'This program is free software.*GPL.*version 2',
                r'http://www\.gnu\.org/licenses/gpl-2\.0'
            ],
            'GPL-3.0': [
                r'GNU GENERAL PUBLIC LICENSE\s+Version 3',
                r'This program is free software.*GPL.*version 3',
                r'http://www\.gnu\.org/licenses/gpl-3\.0'
            ],
            'BSD-3-Clause': [
                r'BSD 3-Clause License',
                r'Redistributions of source code must retain',
                r'Neither the name.*may be used to endorse'
            ],
            'BSD-2-Clause': [
                r'BSD 2-Clause License',
                r'Redistributions of source code must retain.*Redistributions in binary form'
            ]
        }
