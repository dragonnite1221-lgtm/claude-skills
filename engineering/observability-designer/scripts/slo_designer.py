# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from slo_designer_base import *  # noqa: F403,E402
from slo_designer_p0 import main  # noqa: F401,E501
from slo_designer_c0 import SLODesignerMixin0  # noqa: F401
from slo_designer_c1 import SLODesignerMixin1  # noqa: F401
from slo_designer_c2 import SLODesignerMixin2  # noqa: F401
from slo_designer_c3 import SLODesignerMixin3  # noqa: F401
from slo_designer_c4 import SLODesignerMixin4  # noqa: F401
from slo_designer_c5 import SLODesignerMixin5  # noqa: F401


class SLODesigner(SLODesignerMixin0, SLODesignerMixin1, SLODesignerMixin2, SLODesignerMixin3, SLODesignerMixin4, SLODesignerMixin5):
    pass


if __name__ == '__main__':
    main()