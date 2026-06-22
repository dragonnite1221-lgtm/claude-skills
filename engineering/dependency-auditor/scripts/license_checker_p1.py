# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import LicenseInfo, LicenseType, RiskLevel  # noqa: F401,E501


def _mod_cg0_0():
    return {
        'MIT': LicenseInfo(
                name='MIT License',
                spdx_id='MIT',
                license_type=LicenseType.PERMISSIVE,
                risk_level=RiskLevel.LOW,
                description='Very permissive license with minimal restrictions',
                restrictions=['Include copyright notice', 'Include license text'],
                obligations=['Attribution'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'Apache-2.0': LicenseInfo(
                name='Apache License 2.0',
                spdx_id='Apache-2.0',
                license_type=LicenseType.PERMISSIVE,
                risk_level=RiskLevel.LOW,
                description='Permissive license with patent protection',
                restrictions=['Include copyright notice', 'Include license text', 
                             'State changes', 'Include NOTICE file'],
                obligations=['Attribution', 'Patent grant'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': True
                }
            ),
        'BSD-3-Clause': LicenseInfo(
                name='BSD 3-Clause License',
                spdx_id='BSD-3-Clause',
                license_type=LicenseType.PERMISSIVE,
                risk_level=RiskLevel.LOW,
                description='Permissive license with non-endorsement clause',
                restrictions=['Include copyright notice', 'Include license text',
                             'No endorsement using author names'],
                obligations=['Attribution'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'BSD-2-Clause': LicenseInfo(
                name='BSD 2-Clause License',
                spdx_id='BSD-2-Clause',
                license_type=LicenseType.PERMISSIVE,
                risk_level=RiskLevel.LOW,
                description='Very permissive license similar to MIT',
                restrictions=['Include copyright notice', 'Include license text'],
                obligations=['Attribution'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'ISC': LicenseInfo(
                name='ISC License',
                spdx_id='ISC',
                license_type=LicenseType.PERMISSIVE,
                risk_level=RiskLevel.LOW,
                description='Functionally equivalent to MIT license',
                restrictions=['Include copyright notice'],
                obligations=['Attribution'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'MPL-2.0': LicenseInfo(
                name='Mozilla Public License 2.0',
                spdx_id='MPL-2.0',
                license_type=LicenseType.COPYLEFT_WEAK,
                risk_level=RiskLevel.MEDIUM,
                description='File-level copyleft license',
                restrictions=['Disclose source of modified files', 'Include copyright notice',
                             'Include license text', 'State changes'],
                obligations=['Source disclosure (modified files only)'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': True
                }
            ),
        'LGPL-2.1': LicenseInfo(
                name='GNU Lesser General Public License 2.1',
                spdx_id='LGPL-2.1',
                license_type=LicenseType.COPYLEFT_WEAK,
                risk_level=RiskLevel.MEDIUM,
                description='Library-level copyleft license',
                restrictions=['Disclose source of library modifications', 'Include copyright notice',
                             'Include license text', 'Allow relinking'],
                obligations=['Source disclosure (library modifications)', 'Dynamic linking preferred'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'LGPL-3.0': LicenseInfo(
                name='GNU Lesser General Public License 3.0',
                spdx_id='LGPL-3.0',
                license_type=LicenseType.COPYLEFT_WEAK,
                risk_level=RiskLevel.MEDIUM,
                description='Library-level copyleft with patent provisions',
                restrictions=['Disclose source of library modifications', 'Include copyright notice',
                             'Include license text', 'Allow relinking', 'Anti-tivoization'],
                obligations=['Source disclosure (library modifications)', 'Patent grant'],
                compatibility={
                    'commercial': True, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': True
                }
            ),
    }
