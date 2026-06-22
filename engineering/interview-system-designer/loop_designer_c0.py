# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin0:
    """Designs comprehensive interview loops based on role requirements."""
    def __init__(self):
        self.competency_frameworks = self._init_competency_frameworks()
        self.role_templates = self._init_role_templates()
        self.interviewer_skills = self._init_interviewer_skills()
