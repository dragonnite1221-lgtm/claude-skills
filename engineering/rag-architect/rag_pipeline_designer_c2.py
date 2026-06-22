# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402
from rag_pipeline_designer_p0 import ComponentRecommendation, Requirements, Scale  # noqa: F401,E501


class RAGPipelineDesignerMixin2:
    def _recommend_retrieval(self, req: Requirements, scale: Scale) -> ComponentRecommendation:
        """Recommend retrieval strategy."""
        if req.accuracy_priority > 0.8:
            strategy = "hybrid"
            rationale = "Hybrid retrieval for maximum accuracy combining dense and sparse methods"
        elif "technical" in req.document_types or "code" in req.document_types:
            strategy = "hybrid"
            rationale = "Technical content benefits from both semantic and keyword matching"
        elif req.latency_requirement == "real_time":
            strategy = "dense"
            rationale = "Dense retrieval faster for real-time requirements"
        else:
            strategy = "dense"
            rationale = "Dense retrieval suitable for general text search"
        
        return ComponentRecommendation(
            name=strategy,
            type="retrieval", 
            config={
                "strategy": strategy,
                "dense_weight": 0.7 if strategy == "hybrid" else 1.0,
                "sparse_weight": 0.3 if strategy == "hybrid" else 0.0,
                "top_k": 20 if req.accuracy_priority > 0.7 else 10,
                "similarity_threshold": 0.7
            },
            rationale=rationale,
            pros=self._get_retrieval_pros(strategy),
            cons=self._get_retrieval_cons(strategy),
            cost_monthly=0.0
        )
    def _recommend_reranking(self, req: Requirements, scale: Scale) -> Optional[ComponentRecommendation]:
        """Recommend reranking if beneficial."""
        if req.accuracy_priority < 0.6 or req.latency_requirement == "real_time":
            return None
        
        if req.cost_priority > 0.8:
            return None
        
        # Estimate reranking queries per month
        monthly_queries = req.queries_per_day * 30
        cost_per_query = 0.002  # Estimated cost for cross-encoder reranking
        monthly_cost = monthly_queries * cost_per_query
        
        if monthly_cost > req.budget_monthly * 0.3:  # Don't exceed 30% of budget
            return None
        
        return ComponentRecommendation(
            name="cross_encoder_reranking",
            type="reranking",
            config={
                "model": "cross-encoder/ms-marco-MiniLM-L-12-v2",
                "rerank_top_k": 20,
                "return_top_k": 5,
                "batch_size": 16
            },
            rationale="Reranking improves precision for high-accuracy requirements",
            pros=["Higher precision", "Better ranking quality", "Handles complex queries"],
            cons=["Additional latency", "Higher cost", "More complexity"],
            cost_monthly=monthly_cost
        )
    def _recommend_evaluation(self, req: Requirements, scale: Scale) -> ComponentRecommendation:
        """Recommend evaluation framework."""
        return ComponentRecommendation(
            name="comprehensive_evaluation",
            type="evaluation",
            config={
                "metrics": ["precision@k", "recall@k", "mrr", "ndcg"],
                "k_values": [1, 3, 5, 10],
                "faithfulness_check": True,
                "relevance_scoring": True,
                "evaluation_frequency": "weekly" if scale == Scale.LARGE else "monthly",
                "sample_size": min(1000, req.queries_per_day * 7)
            },
            rationale="Comprehensive evaluation essential for production RAG systems",
            pros=["Quality monitoring", "Performance tracking", "Issue detection"],
            cons=["Additional overhead", "Requires ground truth data"],
            cost_monthly=20.0  # Evaluation tooling and compute
        )
