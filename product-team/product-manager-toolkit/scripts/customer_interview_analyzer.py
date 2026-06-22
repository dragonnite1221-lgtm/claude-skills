# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from customer_interview_analyzer_base import *  # noqa: F403,E402
from customer_interview_analyzer_p0 import aggregate_interviews, format_single_interview  # noqa: F401,E501
from customer_interview_analyzer_p1 import main  # noqa: F401,E501
from customer_interview_analyzer_c0 import InterviewAnalyzerMixin0  # noqa: F401
from customer_interview_analyzer_c1 import InterviewAnalyzerMixin1  # noqa: F401
from customer_interview_analyzer_c2 import InterviewAnalyzerMixin2  # noqa: F401


class InterviewAnalyzer(InterviewAnalyzerMixin0, InterviewAnalyzerMixin1, InterviewAnalyzerMixin2):
    pass


if __name__ == "__main__":
    main()
