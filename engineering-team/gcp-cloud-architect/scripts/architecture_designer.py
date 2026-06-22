# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402
from architecture_designer_p0 import ApplicationType, main  # noqa: F401,E501
from architecture_designer_c0 import ArchitectureDesignerMixin0  # noqa: F401
from architecture_designer_c1 import ArchitectureDesignerMixin1  # noqa: F401
from architecture_designer_c2 import ArchitectureDesignerMixin2  # noqa: F401
from architecture_designer_c3 import ArchitectureDesignerMixin3  # noqa: F401
from architecture_designer_c4 import ArchitectureDesignerMixin4  # noqa: F401
from architecture_designer_c5 import ArchitectureDesignerMixin5  # noqa: F401
from architecture_designer_c6 import ArchitectureDesignerMixin6  # noqa: F401
from architecture_designer_c7 import ArchitectureDesignerMixin7  # noqa: F401


class ArchitectureDesigner(ArchitectureDesignerMixin0, ArchitectureDesignerMixin1, ArchitectureDesignerMixin2, ArchitectureDesignerMixin3, ArchitectureDesignerMixin4, ArchitectureDesignerMixin5, ArchitectureDesignerMixin6, ArchitectureDesignerMixin7):
    pass


if __name__ == '__main__':
    main()
