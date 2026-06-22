# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402
from retrieval_evaluator_p0 import Document  # noqa: F401,E501


def load_ground_truth(file_path: str) -> Dict[str, List[str]]:
    """Load ground truth relevance judgments."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(data, dict):
        # Convert all values to lists if they aren't already
        return {k: v if isinstance(v, list) else [v] for k, v in data.items()}
    else:
        raise ValueError("Invalid ground truth format. Expected dict mapping query_id -> relevant_doc_ids.")


def load_corpus(directory: str, extensions: List[str] = None) -> List[Document]:
    """Load document corpus from directory."""
    extensions = extensions or ['.txt', '.md', '.markdown']
    documents = []
    
    corpus_path = Path(directory)
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus directory not found: {directory}")
    
    for file_path in corpus_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if content.strip():
                    # Use filename (without extension) as doc_id
                    doc_id = file_path.stem
                    title = file_path.name
                    
                    doc = Document(doc_id, title, content, str(file_path))
                    documents.append(doc)
                    
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
    
    if not documents:
        raise ValueError(f"No valid documents found in {directory}")
    
    print(f"Loaded {len(documents)} documents from corpus")
    return documents


def generate_recommendations(evaluation_results: Dict[str, Any]) -> List[str]:
    """Generate improvement recommendations based on evaluation results."""
    recommendations = []
    
    metrics = evaluation_results['aggregate_metrics']
    failure_analysis = evaluation_results['failure_analysis']
    
    # Precision-based recommendations
    p1 = metrics.get('mean_precision@1', 0)
    p5 = metrics.get('mean_precision@5', 0)
    
    if p1 < 0.3:
        recommendations.append("LOW PRECISION: Consider implementing query expansion or reranking to improve result quality.")
    
    if p5 < 0.4:
        recommendations.append("RANKING ISSUES: Current ranking may not prioritize relevant documents. Consider BM25 or learning-to-rank models.")
    
    # Recall-based recommendations
    r5 = metrics.get('mean_recall@5', 0)
    r10 = metrics.get('mean_recall@10', 0)
    
    if r5 < 0.5:
        recommendations.append("LOW RECALL: Consider query expansion techniques (synonyms, related terms) to find more relevant documents.")
    
    if r10 - r5 > 0.2:
        recommendations.append("RANKING DEPTH: Many relevant documents found in positions 6-10. Consider increasing default result count.")
    
    # MRR-based recommendations
    mrr = metrics.get('mean_reciprocal_rank', 0)
    if mrr < 0.4:
        recommendations.append("POOR RANKING: First relevant result appears late in rankings. Implement result reranking.")
    
    # Failure pattern recommendations
    zero_results = failure_analysis.get('zero_results_count', 0)
    total_queries = len(evaluation_results['query_results'])
    
    if zero_results > total_queries * 0.1:
        recommendations.append("COVERAGE ISSUES: Many queries return no results. Check for vocabulary mismatch or missing content.")
    
    # Query length analysis
    query_analysis = failure_analysis.get('query_length_analysis', {})
    short_perf = query_analysis.get('short_queries', {}).get('avg_precision@5', 0)
    long_perf = query_analysis.get('long_queries', {}).get('avg_precision@5', 0)
    
    if short_perf < 0.3:
        recommendations.append("SHORT QUERY ISSUES: Brief queries perform poorly. Consider query completion or suggestion features.")
    
    if long_perf > short_perf + 0.2:
        recommendations.append("QUERY PROCESSING: Longer queries perform better. Consider query parsing to extract key terms.")
    
    # General recommendations
    if not recommendations:
        recommendations.append("GOOD PERFORMANCE: System performs well overall. Consider A/B testing incremental improvements.")
    
    return recommendations
