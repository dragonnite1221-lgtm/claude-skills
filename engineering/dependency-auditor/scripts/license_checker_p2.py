# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from license_checker_base import *  # noqa: F403,E402
from license_checker_p0 import LicenseInfo, LicenseType, RiskLevel  # noqa: F401,E501


def _mod_cg0_1():
    return {
        'GPL-2.0': LicenseInfo(
                name='GNU General Public License 2.0',
                spdx_id='GPL-2.0',
                license_type=LicenseType.COPYLEFT_STRONG,
                risk_level=RiskLevel.HIGH,
                description='Strong copyleft requiring full source disclosure',
                restrictions=['Disclose entire source code', 'Include copyright notice',
                             'Include license text', 'Use same license'],
                obligations=['Full source disclosure', 'License compatibility'],
                compatibility={
                    'commercial': False, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'GPL-3.0': LicenseInfo(
                name='GNU General Public License 3.0',
                spdx_id='GPL-3.0',
                license_type=LicenseType.COPYLEFT_STRONG,
                risk_level=RiskLevel.HIGH,
                description='Strong copyleft with patent and hardware provisions',
                restrictions=['Disclose entire source code', 'Include copyright notice',
                             'Include license text', 'Use same license', 'Anti-tivoization'],
                obligations=['Full source disclosure', 'Patent grant', 'License compatibility'],
                compatibility={
                    'commercial': False, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': True
                }
            ),
        'AGPL-3.0': LicenseInfo(
                name='GNU Affero General Public License 3.0',
                spdx_id='AGPL-3.0',
                license_type=LicenseType.COPYLEFT_STRONG,
                risk_level=RiskLevel.CRITICAL,
                description='Network copyleft extending GPL to SaaS',
                restrictions=['Disclose entire source code', 'Include copyright notice',
                             'Include license text', 'Use same license', 'Network use triggers copyleft'],
                obligations=['Full source disclosure', 'Network service source disclosure'],
                compatibility={
                    'commercial': False, 'modification': True, 'distribution': True,
                    'private_use': True, 'patent_grant': True
                }
            ),
        'PROPRIETARY': LicenseInfo(
                name='Proprietary License',
                spdx_id=None,
                license_type=LicenseType.PROPRIETARY,
                risk_level=RiskLevel.HIGH,
                description='Commercial or custom proprietary license',
                restrictions=['Varies by license', 'Often no redistribution',
                             'May require commercial license'],
                obligations=['License agreement compliance', 'Payment obligations'],
                compatibility={
                    'commercial': False, 'modification': False, 'distribution': False,
                    'private_use': True, 'patent_grant': False
                }
            ),
        'UNKNOWN': LicenseInfo(
                name='Unknown License',
                spdx_id=None,
                license_type=LicenseType.UNKNOWN,
                risk_level=RiskLevel.CRITICAL,
                description='No license detected or ambiguous licensing',
                restrictions=['Unknown', 'Assume no rights granted'],
                obligations=['Investigate and clarify licensing'],
                compatibility={
                    'commercial': False, 'modification': False, 'distribution': False,
                    'private_use': False, 'patent_grant': False
                }
            ),
    }
