# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402
from rag_pipeline_designer_p0 import ComponentRecommendation, PipelineDesign, Requirements, Scale  # noqa: F401,E501


class RAGPipelineDesignerMixin0:
    """Main pipeline designer class."""
    def __init__(self):
        self.embedding_models = self._load_embedding_models()
        self.vector_databases = self._load_vector_databases()
        self.chunking_strategies = self._load_chunking_strategies()
    def design_pipeline(self, requirements: Requirements) -> PipelineDesign:
        """Design complete RAG pipeline based on requirements."""
        print(f"Designing RAG pipeline for {requirements.document_count:,} documents...")
        
        # Determine system scale
        scale = self._determine_scale(requirements)
        print(f"System scale: {scale.value}")
        
        # Design each component
        chunking = self._recommend_chunking(requirements, scale)
        embedding = self._recommend_embedding(requirements, scale)  
        vector_db = self._recommend_vector_db(requirements, scale)
        retrieval = self._recommend_retrieval(requirements, scale)
        reranking = self._recommend_reranking(requirements, scale)
        evaluation = self._recommend_evaluation(requirements, scale)
        
        # Calculate total cost
        total_cost = (chunking.cost_monthly + embedding.cost_monthly + 
                     vector_db.cost_monthly + retrieval.cost_monthly + 
                     evaluation.cost_monthly)
        if reranking:
            total_cost += reranking.cost_monthly
        
        # Generate architecture diagram
        architecture = self._generate_architecture_diagram(
            chunking, embedding, vector_db, retrieval, reranking, evaluation
        )
        
        # Generate configuration templates
        configs = self._generate_config_templates(
            chunking, embedding, vector_db, retrieval, reranking, evaluation
        )
        
        return PipelineDesign(
            chunking=chunking,
            embedding=embedding,
            vector_db=vector_db,
            retrieval=retrieval,
            reranking=reranking,
            evaluation=evaluation,
            total_cost=total_cost,
            architecture_diagram=architecture,
            config_templates=configs
        )
    def _determine_scale(self, req: Requirements) -> Scale:
        """Determine system scale based on requirements."""
        if req.document_count < 1_000_000 and req.queries_per_day < 1_000:
            return Scale.SMALL
        elif req.document_count < 100_000_000 and req.queries_per_day < 100_000:
            return Scale.MEDIUM
        else:
            return Scale.LARGE
    def _recommend_chunking(self, req: Requirements, scale: Scale) -> ComponentRecommendation:
        """Recommend chunking strategy."""
        doc_types = set(req.document_types)
        
        if "code" in doc_types:
            strategy = "semantic_code_aware"
            config = {"max_size": 1000, "preserve_functions": True, "overlap": 50}
            rationale = "Code documents benefit from function/class boundary awareness"
        elif "technical" in doc_types or "scientific" in doc_types:
            strategy = "semantic_heading_aware" 
            config = {"max_size": 1500, "heading_weight": 2.0, "overlap": 100}
            rationale = "Technical documents have clear hierarchical structure"
        elif len(doc_types) > 2 or "mixed" in doc_types:
            strategy = "adaptive_chunking"
            config = {"strategies": ["paragraph", "sentence", "fixed"], "auto_select": True}
            rationale = "Mixed document types require adaptive strategy selection"
        else:
            if req.avg_document_size > 5000:
                strategy = "paragraph_based"
                config = {"max_size": 2000, "min_paragraph_size": 100}
                rationale = "Large documents benefit from paragraph-based chunking"
            else:
                strategy = "sentence_based"  
                config = {"max_size": 1000, "sentence_overlap": 1}
                rationale = "Small to medium documents work well with sentence chunking"
        
        return ComponentRecommendation(
            name=strategy,
            type="chunking",
            config=config,
            rationale=rationale,
            pros=self._get_chunking_pros(strategy),
            cons=self._get_chunking_cons(strategy),
            cost_monthly=0.0  # Processing cost only
        )
