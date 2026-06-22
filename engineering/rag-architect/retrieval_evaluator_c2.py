# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402


class RetrievalEvaluatorMixin2:
    def _generate_summary(self, metrics: Dict[str, float], num_queries: int) -> str:
        """Generate human-readable evaluation summary."""
        summary = f"Evaluation Summary ({num_queries} queries):\n"
        summary += f"{'='*50}\n"
        
        # Key metrics
        p1 = metrics.get('mean_precision@1', 0)
        p5 = metrics.get('mean_precision@5', 0)
        r5 = metrics.get('mean_recall@5', 0)
        mrr = metrics.get('mean_reciprocal_rank', 0)
        ndcg5 = metrics.get('mean_ndcg@5', 0)
        
        summary += f"Precision@1:  {p1:.3f} ({p1*100:.1f}%)\n"
        summary += f"Precision@5:  {p5:.3f} ({p5*100:.1f}%)\n"
        summary += f"Recall@5:     {r5:.3f} ({r5*100:.1f}%)\n"
        summary += f"MRR:          {mrr:.3f}\n"
        summary += f"NDCG@5:       {ndcg5:.3f}\n"
        
        # Performance assessment
        summary += f"\nPerformance Assessment:\n"
        if p1 >= 0.7:
            summary += "✓ Excellent precision - most queries return relevant results first\n"
        elif p1 >= 0.5:
            summary += "○ Good precision - many queries return relevant results first\n"
        else:
            summary += "✗ Poor precision - few queries return relevant results first\n"
        
        if r5 >= 0.8:
            summary += "✓ Excellent recall - finding most relevant documents\n"
        elif r5 >= 0.6:
            summary += "○ Good recall - finding many relevant documents\n"
        else:
            summary += "✗ Poor recall - missing many relevant documents\n"
        
        return summary
