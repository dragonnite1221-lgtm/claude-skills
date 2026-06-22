# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_pipeline_designer_base import *  # noqa: F403,E402


class Scale(Enum):
    """System scale categories."""
    SMALL = "small"      # < 1M documents, < 1K queries/day
    MEDIUM = "medium"    # 1M-100M documents, 1K-100K queries/day  
    LARGE = "large"      # 100M+ documents, 100K+ queries/day


class DocumentType(Enum):
    """Document type categories."""
    TEXT = "text"                # Plain text, articles
    TECHNICAL = "technical"      # Documentation, manuals
    CODE = "code"               # Source code files
    SCIENTIFIC = "scientific"    # Research papers, journals
    LEGAL = "legal"             # Legal documents, contracts
    MIXED = "mixed"             # Multiple document types


class Latency(Enum):
    """Latency requirements."""
    REAL_TIME = "real_time"      # < 100ms
    INTERACTIVE = "interactive"   # < 500ms  
    BATCH = "batch"              # > 1s acceptable


@dataclass
class Requirements:
    """RAG system requirements."""
    document_types: List[str]
    document_count: int
    avg_document_size: int  # characters
    queries_per_day: int
    query_patterns: List[str]  # e.g., ["factual", "conversational", "analytical"]
    latency_requirement: str
    budget_monthly: float  # USD
    accuracy_priority: float  # 0-1 scale
    cost_priority: float     # 0-1 scale
    maintenance_complexity: str  # "low", "medium", "high"


@dataclass
class ComponentRecommendation:
    """Recommendation for a pipeline component."""
    name: str
    type: str
    config: Dict[str, Any]
    rationale: str
    pros: List[str]
    cons: List[str]
    cost_monthly: float


@dataclass
class PipelineDesign:
    """Complete RAG pipeline design."""
    chunking: ComponentRecommendation
    embedding: ComponentRecommendation  
    vector_db: ComponentRecommendation
    retrieval: ComponentRecommendation
    reranking: Optional[ComponentRecommendation]
    evaluation: ComponentRecommendation
    total_cost: float
    architecture_diagram: str
    config_templates: Dict[str, Any]


def load_requirements(file_path: str) -> Requirements:
    """Load requirements from JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return Requirements(**data)


def save_design(design: PipelineDesign, output_path: str):
    """Save pipeline design to JSON file."""
    # Convert to dict for JSON serialization
    design_dict = {}
    
    for field_name in design.__dataclass_fields__:
        value = getattr(design, field_name)
        if isinstance(value, ComponentRecommendation):
            design_dict[field_name] = asdict(value)
        elif value is None:
            design_dict[field_name] = None
        else:
            design_dict[field_name] = value
    
    with open(output_path, 'w') as f:
        json.dump(design_dict, f, indent=2)


def print_design_summary(design: PipelineDesign):
    """Print human-readable design summary."""
    print("\n" + "="*60)
    print("RAG PIPELINE DESIGN SUMMARY")
    print("="*60)
    
    print(f"\n💰 Total Monthly Cost: ${design.total_cost:.2f}")
    
    print(f"\n🔧 Component Recommendations:")
    components = [design.chunking, design.embedding, design.vector_db, 
                 design.retrieval, design.reranking, design.evaluation]
    
    for component in components:
        if component:
            print(f"\n  {component.type.upper()}: {component.name}")
            print(f"    Rationale: {component.rationale}")
            if component.cost_monthly > 0:
                print(f"    Monthly Cost: ${component.cost_monthly:.2f}")
    
    print(f"\n📊 Architecture Diagram:")
    print(design.architecture_diagram)
