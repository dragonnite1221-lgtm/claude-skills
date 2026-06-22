# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402
from retrieval_evaluator_p0 import Document  # noqa: F401,E501
from retrieval_evaluator_p1 import TFIDFRetriever, load_queries  # noqa: F401,E501
from retrieval_evaluator_p2 import generate_recommendations, load_corpus, load_ground_truth  # noqa: F401,E501
from retrieval_evaluator_p3 import main  # noqa: F401,E501
from retrieval_evaluator_c0 import RetrievalEvaluatorMixin0  # noqa: F401
from retrieval_evaluator_c1 import RetrievalEvaluatorMixin1  # noqa: F401
from retrieval_evaluator_c2 import RetrievalEvaluatorMixin2  # noqa: F401


class RetrievalEvaluator(RetrievalEvaluatorMixin0, RetrievalEvaluatorMixin1, RetrievalEvaluatorMixin2):
    pass


if __name__ == '__main__':
    exit(main())