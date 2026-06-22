# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402
from deployment_manager_p0 import main  # noqa: F401,E501
from deployment_manager_c0 import DeploymentManagerMixin0  # noqa: F401
from deployment_manager_c1 import DeploymentManagerMixin1  # noqa: F401
from deployment_manager_c2 import DeploymentManagerMixin2  # noqa: F401
from deployment_manager_c3 import DeploymentManagerMixin3  # noqa: F401
from deployment_manager_c4 import DeploymentManagerMixin4  # noqa: F401
from deployment_manager_c5 import DeploymentManagerMixin5  # noqa: F401


class DeploymentManager(DeploymentManagerMixin0, DeploymentManagerMixin1, DeploymentManagerMixin2, DeploymentManagerMixin3, DeploymentManagerMixin4, DeploymentManagerMixin5):
    pass


if __name__ == '__main__':
    main()
