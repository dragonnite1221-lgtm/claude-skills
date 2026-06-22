# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402


class RetrievalEvaluatorMixin1:
    def _calculate_ndcg(self, retrieved_docs: List[str], relevant_docs: Set[str]) -> float:
        """Calculate Normalized Discounted Cumulative Gain."""
        if not retrieved_docs:
            return 0.0
        
        # DCG calculation
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_docs):
            relevance = 1 if doc_id in relevant_docs else 0
            dcg += relevance / math.log2(i + 2)  # +2 because log2(1) = 0
        
        # IDCG calculation (ideal DCG)
        ideal_relevances = [1] * min(len(relevant_docs), len(retrieved_docs))
        idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevances))
        
        return dcg / idcg if idcg > 0 else 0.0
    def _safe_mean(self, values: List[float]) -> float:
        """Calculate mean, handling empty lists."""
        return sum(values) / len(values) if values else 0.0
    def _analyze_failures(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze common failure patterns."""
        total_queries = len(query_results)
        
        # Identify queries with poor performance
        poor_precision_queries = []
        poor_recall_queries = []
        zero_results_queries = []
        
        for result in query_results:
            metrics = result['metrics']
            
            if metrics.get('precision@5', 0) < 0.2:
                poor_precision_queries.append(result)
            
            if metrics.get('recall@5', 0) < 0.3:
                poor_recall_queries.append(result)
            
            if result['retrieved_count'] == 0:
                zero_results_queries.append(result)
        
        # Analyze query characteristics
        query_length_analysis = self._analyze_query_lengths(query_results)
        
        return {
            'poor_precision_count': len(poor_precision_queries),
            'poor_recall_count': len(poor_recall_queries),
            'zero_results_count': len(zero_results_queries),
            'poor_precision_examples': poor_precision_queries[:3],
            'poor_recall_examples': poor_recall_queries[:3],
            'query_length_analysis': query_length_analysis,
            'common_failure_patterns': self._identify_failure_patterns(query_results)
        }
    def _analyze_query_lengths(self, query_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze relationship between query length and performance."""
        short_queries = []  # <= 3 words
        medium_queries = []  # 4-7 words  
        long_queries = []  # >= 8 words
        
        for result in query_results:
            query_length = len(result['query'].split())
            precision = result['metrics'].get('precision@5', 0)
            
            if query_length <= 3:
                short_queries.append(precision)
            elif query_length <= 7:
                medium_queries.append(precision)
            else:
                long_queries.append(precision)
        
        return {
            'short_queries': {
                'count': len(short_queries),
                'avg_precision@5': self._safe_mean(short_queries)
            },
            'medium_queries': {
                'count': len(medium_queries),
                'avg_precision@5': self._safe_mean(medium_queries)
            },
            'long_queries': {
                'count': len(long_queries),
                'avg_precision@5': self._safe_mean(long_queries)
            }
        }
    def _identify_failure_patterns(self, query_results: List[Dict[str, Any]]) -> List[str]:
        """Identify common patterns in failed queries."""
        patterns = []
        
        # Check for vocabulary mismatch
        vocab_mismatch_count = 0
        for result in query_results:
            if result['metrics'].get('precision@1', 0) == 0 and result['retrieved_count'] > 0:
                vocab_mismatch_count += 1
        
        if vocab_mismatch_count > len(query_results) * 0.2:
            patterns.append(f"Vocabulary mismatch: {vocab_mismatch_count} queries may have vocabulary mismatch issues")
        
        # Check for specificity issues
        zero_results = sum(1 for r in query_results if r['retrieved_count'] == 0)
        if zero_results > len(query_results) * 0.1:
            patterns.append(f"Query specificity: {zero_results} queries returned no results (may be too specific)")
        
        # Check for recall issues
        low_recall = sum(1 for r in query_results if r['metrics'].get('recall@10', 0) < 0.5)
        if low_recall > len(query_results) * 0.3:
            patterns.append(f"Low recall: {low_recall} queries have recall@10 < 0.5 (missing relevant documents)")
        
        return patterns
