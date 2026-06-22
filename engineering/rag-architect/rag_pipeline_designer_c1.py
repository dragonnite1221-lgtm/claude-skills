# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402
from rag_pipeline_designer_p0 import ComponentRecommendation, Requirements, Scale  # noqa: F401,E501


class RAGPipelineDesignerMixin1:
    def _recommend_embedding(self, req: Requirements, scale: Scale) -> ComponentRecommendation:
        """Recommend embedding model."""
        doc_types = set(req.document_types)
        
        # Consider accuracy vs cost priority
        high_accuracy = req.accuracy_priority > 0.7
        cost_sensitive = req.cost_priority > 0.6
        
        if "code" in doc_types:
            if high_accuracy and not cost_sensitive:
                model = "openai-code-search-ada-002"
                cost_per_1k_tokens = 0.0001
                dimensions = 1536
            else:
                model = "sentence-transformers/code-bert-base"
                cost_per_1k_tokens = 0.0  # Self-hosted
                dimensions = 768
        elif "scientific" in doc_types:
            if high_accuracy:
                model = "openai-text-embedding-ada-002"
                cost_per_1k_tokens = 0.0001
                dimensions = 1536
            else:
                model = "sentence-transformers/scibert-nli" 
                cost_per_1k_tokens = 0.0
                dimensions = 768
        else:
            if cost_sensitive or scale == Scale.SMALL:
                model = "sentence-transformers/all-MiniLM-L6-v2"
                cost_per_1k_tokens = 0.0
                dimensions = 384
            elif high_accuracy:
                model = "openai-text-embedding-ada-002"
                cost_per_1k_tokens = 0.0001  
                dimensions = 1536
            else:
                model = "sentence-transformers/all-mpnet-base-v2"
                cost_per_1k_tokens = 0.0
                dimensions = 768
        
        # Calculate monthly embedding cost
        total_tokens = req.document_count * (req.avg_document_size / 4)  # ~4 chars per token
        query_tokens = req.queries_per_day * 30 * 20  # ~20 tokens per query per month
        monthly_cost = (total_tokens + query_tokens) * cost_per_1k_tokens / 1000
        
        return ComponentRecommendation(
            name=model,
            type="embedding",
            config={
                "model": model,
                "dimensions": dimensions,
                "batch_size": 100 if scale == Scale.SMALL else 1000,
                "cache_embeddings": True
            },
            rationale=f"Selected for {doc_types} with accuracy priority {req.accuracy_priority}",
            pros=self._get_embedding_pros(model),
            cons=self._get_embedding_cons(model),
            cost_monthly=monthly_cost
        )
    def _recommend_vector_db(self, req: Requirements, scale: Scale) -> ComponentRecommendation:
        """Recommend vector database."""
        if scale == Scale.SMALL and req.cost_priority > 0.7:
            db = "chroma"
            cost = 0.0
            rationale = "Local/embedded database suitable for small scale and cost optimization"
        elif scale == Scale.SMALL and req.maintenance_complexity == "low":
            db = "pgvector"
            cost = 50.0  # PostgreSQL hosting
            rationale = "Leverage existing PostgreSQL infrastructure"
        elif scale == Scale.LARGE or req.latency_requirement == "real_time":
            db = "pinecone"
            vectors = req.document_count * 2  # Account for chunking
            cost = max(70, vectors * 0.00005)  # $70 base + $0.00005 per vector
            rationale = "Managed service with excellent performance for large scale"
        elif req.maintenance_complexity == "low":
            db = "weaviate_cloud"
            vectors = req.document_count * 2
            cost = max(25, vectors * 0.00003)
            rationale = "Managed Weaviate with good balance of features and cost"
        else:
            db = "qdrant"
            cost = 100.0  # Self-hosted infrastructure estimate
            rationale = "High performance self-hosted option with good scaling"
        
        return ComponentRecommendation(
            name=db,
            type="vector_database",
            config=self._get_vector_db_config(db, req, scale),
            rationale=rationale,
            pros=self._get_vector_db_pros(db),
            cons=self._get_vector_db_cons(db),
            cost_monthly=cost
        )
