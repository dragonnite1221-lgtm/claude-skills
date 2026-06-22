# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_evaluator_base import *  # noqa: F403,E402
# fmt: off
from rag_evaluator_p1 import RAGEvaluationReport  # noqa: E402,E501
# fmt: on


def generate_recommendations(report: RAGEvaluationReport) -> List[str]:
    """Generate actionable recommendations based on evaluation"""
    recommendations = []

    if report.avg_context_relevance < 0.8:
        recommendations.append(
            f"Context relevance ({report.avg_context_relevance:.2f}) is below target (0.80). "
            "Consider: improving chunking strategy, adding metadata filtering, or using hybrid search."
        )

    if report.avg_faithfulness < 0.95:
        recommendations.append(
            f"Faithfulness ({report.avg_faithfulness:.2f}) is below target (0.95). "
            "Consider: adding source citations, implementing fact-checking, or adjusting temperature."
        )

    if report.avg_groundedness < 0.85:
        recommendations.append(
            f"Groundedness ({report.avg_groundedness:.2f}) is below target (0.85). "
            "Consider: using more restrictive prompts, adding 'only use provided context' instructions."
        )

    if report.coverage < 0.9:
        recommendations.append(
            f"Coverage ({report.coverage:.2f}) indicates some questions lack relevant context. "
            "Consider: expanding document corpus, improving embedding model, or adding fallback responses."
        )

    retrieval = report.retrieval_metrics
    if retrieval.get('precision_at_k', 0) < 0.7:
        recommendations.append(
            "Retrieval precision is low. Consider: re-ranking retrieved documents, "
            "using cross-encoder for reranking, or adjusting similarity threshold."
        )

    if not recommendations:
        recommendations.append("All metrics meet targets. Consider A/B testing new improvements.")

    return recommendations
