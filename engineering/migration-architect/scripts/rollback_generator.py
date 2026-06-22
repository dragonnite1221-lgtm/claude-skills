# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rollback_generator_base import *  # noqa: F403,E402
from rollback_generator_p0 import CommunicationTemplate, DataRecoveryPlan, RollbackPhase, RollbackRunbook, RollbackStep, RollbackTrigger, RollbackTriggerCondition, RollbackUrgency  # noqa: F401,E501
from rollback_generator_p1 import main  # noqa: F401,E501
from rollback_generator_c0 import RollbackGeneratorMixin0  # noqa: F401
from rollback_generator_c1 import RollbackGeneratorMixin1  # noqa: F401
from rollback_generator_c2 import RollbackGeneratorMixin2  # noqa: F401
from rollback_generator_c3 import RollbackGeneratorMixin3  # noqa: F401
from rollback_generator_c4 import RollbackGeneratorMixin4  # noqa: F401
from rollback_generator_c5 import RollbackGeneratorMixin5  # noqa: F401
from rollback_generator_c6 import RollbackGeneratorMixin6  # noqa: F401
from rollback_generator_c7 import RollbackGeneratorMixin7  # noqa: F401
from rollback_generator_c8 import RollbackGeneratorMixin8  # noqa: F401


class RollbackGenerator(RollbackGeneratorMixin0, RollbackGeneratorMixin1, RollbackGeneratorMixin2, RollbackGeneratorMixin3, RollbackGeneratorMixin4, RollbackGeneratorMixin5, RollbackGeneratorMixin6, RollbackGeneratorMixin7, RollbackGeneratorMixin8):
    pass


if __name__ == "__main__":
    sys.exit(main())