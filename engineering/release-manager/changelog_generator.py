# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from changelog_generator_base import *  # noqa: F403,E402
from changelog_generator_p0 import ConventionalCommit  # noqa: F401,E501
from changelog_generator_p1 import main  # noqa: F401,E501
from changelog_generator_c0 import ChangelogGeneratorMixin0  # noqa: F401
from changelog_generator_c1 import ChangelogGeneratorMixin1  # noqa: F401
from changelog_generator_c2 import ChangelogGeneratorMixin2  # noqa: F401


class ChangelogGenerator(ChangelogGeneratorMixin0, ChangelogGeneratorMixin1, ChangelogGeneratorMixin2):
    pass


if __name__ == '__main__':
    main()