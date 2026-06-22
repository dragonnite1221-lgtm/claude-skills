# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402
from retrieval_evaluator_p1 import TFIDFRetriever  # noqa: F401,E501


class RetrievalEvaluatorMixin0:
    """Evaluates retrieval system performance using standard IR metrics."""
    def __init__(self):
        self.metrics = {}
    def evaluate(self, queries: List[Dict[str, Any]], ground_truth: Dict[str, List[str]], 
                 retriever: TFIDFRetriever, k_values: List[int] = None) -> Dict[str, Any]:
        """Evaluate retrieval performance."""
        k_values = k_values or [1, 3, 5, 10]
        
        print(f"Evaluating retrieval performance for {len(queries)} queries...")
        
        query_results = []
        all_precision_at_k = {k: [] for k in k_values}
        all_recall_at_k = {k: [] for k in k_values}
        all_ndcg_at_k = {k: [] for k in k_values}
        reciprocal_ranks = []
        
        for query_data in queries:
            query_id = query_data['id']
            query_text = query_data['query']
            
            # Get ground truth for this query
            relevant_docs = set(ground_truth.get(query_id, []))
            
            if not relevant_docs:
                print(f"Warning: No ground truth found for query {query_id}")
                continue
            
            # Retrieve documents
            max_k = max(k_values)
            results = retriever.search(query_text, max_k)
            retrieved_doc_ids = [doc_id for doc_id, _ in results]
            
            # Calculate metrics for this query
            query_metrics = {}
            
            # Precision@K and Recall@K
            for k in k_values:
                retrieved_at_k = set(retrieved_doc_ids[:k])
                relevant_retrieved = retrieved_at_k & relevant_docs
                
                precision = len(relevant_retrieved) / len(retrieved_at_k) if retrieved_at_k else 0
                recall = len(relevant_retrieved) / len(relevant_docs) if relevant_docs else 0
                
                query_metrics[f'precision@{k}'] = precision
                query_metrics[f'recall@{k}'] = recall
                
                all_precision_at_k[k].append(precision)
                all_recall_at_k[k].append(recall)
            
            # Mean Reciprocal Rank (MRR)
            reciprocal_rank = self._calculate_reciprocal_rank(retrieved_doc_ids, relevant_docs)
            query_metrics['reciprocal_rank'] = reciprocal_rank
            reciprocal_ranks.append(reciprocal_rank)
            
            # NDCG@K
            for k in k_values:
                ndcg = self._calculate_ndcg(retrieved_doc_ids[:k], relevant_docs)
                query_metrics[f'ndcg@{k}'] = ndcg
                all_ndcg_at_k[k].append(ndcg)
            
            # Store query-level results
            query_results.append({
                'query_id': query_id,
                'query': query_text,
                'relevant_count': len(relevant_docs),
                'retrieved_count': len(retrieved_doc_ids),
                'metrics': query_metrics,
                'retrieved_docs': results[:5],  # Top 5 for analysis
                'relevant_docs': list(relevant_docs)
            })
        
        # Calculate aggregate metrics
        aggregate_metrics = {}
        
        for k in k_values:
            aggregate_metrics[f'mean_precision@{k}'] = self._safe_mean(all_precision_at_k[k])
            aggregate_metrics[f'mean_recall@{k}'] = self._safe_mean(all_recall_at_k[k])
            aggregate_metrics[f'mean_ndcg@{k}'] = self._safe_mean(all_ndcg_at_k[k])
        
        aggregate_metrics['mean_reciprocal_rank'] = self._safe_mean(reciprocal_ranks)
        
        # Failure analysis
        failure_analysis = self._analyze_failures(query_results)
        
        return {
            'aggregate_metrics': aggregate_metrics,
            'query_results': query_results,
            'failure_analysis': failure_analysis,
            'evaluation_summary': self._generate_summary(aggregate_metrics, len(queries))
        }
    def _calculate_reciprocal_rank(self, retrieved_docs: List[str], relevant_docs: Set[str]) -> float:
        """Calculate reciprocal rank - 1/rank of first relevant document."""
        for i, doc_id in enumerate(retrieved_docs):
            if doc_id in relevant_docs:
                return 1.0 / (i + 1)
        return 0.0
