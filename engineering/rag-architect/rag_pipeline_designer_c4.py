# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402
from rag_pipeline_designer_p0 import Requirements, Scale  # noqa: F401,E501


class RAGPipelineDesignerMixin4:
    def _load_chunking_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Load chunking strategy specifications."""
        return {
            "fixed_size": {"complexity": "low", "quality": "medium"},
            "sentence_based": {"complexity": "medium", "quality": "good"}, 
            "paragraph_based": {"complexity": "medium", "quality": "good"},
            "semantic_heading_aware": {"complexity": "high", "quality": "excellent"}
        }
    def _get_vector_db_config(self, db: str, req: Requirements, scale: Scale) -> Dict[str, Any]:
        """Get vector database configuration."""
        base_config = {
            "collection_name": "rag_documents",
            "distance_metric": "cosine",
            "index_type": "hnsw"
        }
        
        if db == "pinecone":
            base_config.update({
                "environment": "us-east1-gcp",
                "replicas": 1 if scale == Scale.SMALL else 2,
                "shards": 1 if scale != Scale.LARGE else 3
            })
        elif db == "qdrant":
            base_config.update({
                "memory_mapping": True,
                "quantization": scale == Scale.LARGE,
                "replication_factor": 1 if scale == Scale.SMALL else 2
            })
        
        return base_config
    def _get_chunking_pros(self, strategy: str) -> List[str]:
        """Get pros for chunking strategy."""
        pros_map = {
            "semantic_heading_aware": ["Preserves document structure", "High semantic coherence", "Good for technical docs"],
            "paragraph_based": ["Respects natural boundaries", "Good balance", "Readable chunks"],
            "sentence_based": ["Natural language boundaries", "Consistent quality", "Good for general text"],
            "fixed_size": ["Predictable sizes", "Simple implementation", "Consistent processing"],
            "adaptive_chunking": ["Handles mixed content", "Optimizes per document", "Best quality"]
        }
        return pros_map.get(strategy, ["Good general purpose strategy"])
    def _get_chunking_cons(self, strategy: str) -> List[str]:
        """Get cons for chunking strategy."""
        cons_map = {
            "semantic_heading_aware": ["Complex implementation", "May create large chunks", "Document-dependent"],
            "paragraph_based": ["Variable sizes", "May break context", "Document-dependent"],
            "sentence_based": ["May create small chunks", "Sentence detection issues", "Variable sizes"],
            "fixed_size": ["Breaks semantic boundaries", "May split sentences", "Context loss"],
            "adaptive_chunking": ["High complexity", "Slower processing", "Harder to debug"]
        }
        return cons_map.get(strategy, ["May not fit all use cases"])
    def _get_embedding_pros(self, model: str) -> List[str]:
        """Get pros for embedding model."""
        if "openai" in model:
            return ["High quality", "Regular updates", "Good performance"]
        elif "all-mpnet" in model:
            return ["High quality", "Free to use", "Good balance"]
        elif "MiniLM" in model:
            return ["Fast processing", "Small size", "Good for real-time"]
        else:
            return ["Specialized for domain", "Good performance"]
    def _get_embedding_cons(self, model: str) -> List[str]:
        """Get cons for embedding model."""
        if "openai" in model:
            return ["API costs", "Vendor lock-in", "Rate limits"]
        elif "sentence-transformers" in model:
            return ["Self-hosting required", "Model updates needed", "GPU beneficial"]
        else:
            return ["May require fine-tuning", "Domain-specific"]
    def _get_vector_db_pros(self, db: str) -> List[str]:
        """Get pros for vector database."""
        pros_map = {
            "pinecone": ["Fully managed", "Excellent performance", "Auto-scaling"],
            "weaviate": ["Rich features", "GraphQL API", "Multi-modal"],
            "qdrant": ["High performance", "Rust-based", "Good scaling"],
            "chroma": ["Simple setup", "Free", "Good for development"],
            "pgvector": ["SQL integration", "ACID compliance", "Familiar"]
        }
        return pros_map.get(db, ["Good performance"])
    def _get_vector_db_cons(self, db: str) -> List[str]:
        """Get cons for vector database."""
        cons_map = {
            "pinecone": ["Expensive", "Vendor lock-in", "Limited customization"],
            "weaviate": ["Complex setup", "Learning curve", "Resource intensive"],
            "qdrant": ["Self-managed", "Smaller community", "Setup complexity"],
            "chroma": ["Limited scaling", "Not production-ready", "Basic features"],
            "pgvector": ["PostgreSQL knowledge needed", "Less specialized", "Manual optimization"]
        }
        return cons_map.get(db, ["Requires maintenance"])
    def _get_retrieval_pros(self, strategy: str) -> List[str]:
        """Get pros for retrieval strategy."""
        pros_map = {
            "dense": ["Semantic understanding", "Good for paraphrases", "Fast"],
            "sparse": ["Exact matching", "Interpretable", "Good for keywords"], 
            "hybrid": ["Best of both", "High accuracy", "Robust"]
        }
        return pros_map.get(strategy, ["Good performance"])
    def _get_retrieval_cons(self, strategy: str) -> List[str]:
        """Get cons for retrieval strategy."""
        cons_map = {
            "dense": ["May miss exact matches", "Embedding dependent", "Less interpretable"],
            "sparse": ["Vocabulary mismatch", "No semantic understanding", "Synonym issues"],
            "hybrid": ["More complex", "Tuning required", "Higher latency"]
        }
        return cons_map.get(strategy, ["May require tuning"])
