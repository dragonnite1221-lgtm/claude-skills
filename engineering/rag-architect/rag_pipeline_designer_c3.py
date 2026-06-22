# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402
from rag_pipeline_designer_p0 import ComponentRecommendation  # noqa: F401,E501


class RAGPipelineDesignerMixin3:
    def _generate_architecture_diagram(self, chunking: ComponentRecommendation, 
                                     embedding: ComponentRecommendation,
                                     vector_db: ComponentRecommendation,
                                     retrieval: ComponentRecommendation,
                                     reranking: Optional[ComponentRecommendation],
                                     evaluation: ComponentRecommendation) -> str:
        """Generate Mermaid architecture diagram."""
        
        diagram = """```mermaid
graph TB
    %% Document Processing Pipeline
    A[Document Corpus] --> B[Document Chunking]
    B --> C[Embedding Generation]
    C --> D[Vector Database Storage]
    
    %% Query Processing Pipeline  
    E[User Query] --> F[Query Processing]
    F --> G[Vector Search]
    D --> G
    G --> H[Retrieved Chunks]
"""
        
        if reranking:
            diagram += "    H --> I[Reranking]\n    I --> J[Final Results]\n"
        else:
            diagram += "    H --> J[Final Results]\n"
        
        diagram += """    
    %% Evaluation Pipeline
    J --> K[Response Generation]
    K --> L[Evaluation Metrics]
    
    %% Component Details
    B -.-> B1[Strategy: """ + chunking.name + """]
    C -.-> C1[Model: """ + embedding.name + """]
    D -.-> D1[Database: """ + vector_db.name + """]
    G -.-> G1[Method: """ + retrieval.name + """]
"""
        
        if reranking:
            diagram += "    I -.-> I1[Model: " + reranking.name + "]\n"
        
        diagram += "    L -.-> L1[Framework: " + evaluation.name + "]\n```"
        
        return diagram
    def _generate_config_templates(self, *components) -> Dict[str, Any]:
        """Generate configuration templates for all components."""
        configs = {}
        
        for component in components:
            if component:
                configs[component.type] = {
                    "component": component.name,
                    "config": component.config,
                    "rationale": component.rationale
                }
        
        # Add deployment configuration
        configs["deployment"] = {
            "infrastructure": "cloud" if any("pinecone" in str(c.name) for c in components if c) else "hybrid",
            "scaling": {
                "auto_scaling": True,
                "min_replicas": 1,
                "max_replicas": 10
            },
            "monitoring": {
                "metrics": ["latency", "throughput", "accuracy"],
                "alerts": ["high_latency", "low_accuracy", "service_down"]
            }
        }
        
        return configs
    def _load_embedding_models(self) -> Dict[str, Dict[str, Any]]:
        """Load embedding model specifications."""
        return {
            "openai-text-embedding-ada-002": {
                "dimensions": 1536,
                "cost_per_1k_tokens": 0.0001,
                "quality": "high",
                "speed": "medium"
            },
            "sentence-transformers/all-mpnet-base-v2": {
                "dimensions": 768, 
                "cost_per_1k_tokens": 0.0,
                "quality": "high",
                "speed": "medium"
            },
            "sentence-transformers/all-MiniLM-L6-v2": {
                "dimensions": 384,
                "cost_per_1k_tokens": 0.0,
                "quality": "medium",
                "speed": "fast"
            }
        }
    def _load_vector_databases(self) -> Dict[str, Dict[str, Any]]:
        """Load vector database specifications."""
        return {
            "pinecone": {"managed": True, "scaling": "excellent", "cost": "high"},
            "weaviate": {"managed": False, "scaling": "good", "cost": "medium"},
            "qdrant": {"managed": False, "scaling": "excellent", "cost": "low"},
            "chroma": {"managed": False, "scaling": "poor", "cost": "free"},
            "pgvector": {"managed": False, "scaling": "good", "cost": "medium"}
        }
