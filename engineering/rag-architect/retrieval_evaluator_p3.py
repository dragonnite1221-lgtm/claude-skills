# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402
from retrieval_evaluator_p1 import TFIDFRetriever, load_queries  # noqa: F401,E501
from retrieval_evaluator_p2 import generate_recommendations, load_corpus, load_ground_truth  # noqa: F401,E501


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='Evaluate retrieval system performance')
    parser.add_argument('queries', help='JSON file containing queries')
    parser.add_argument('corpus', help='Directory containing document corpus')
    parser.add_argument('ground_truth', help='JSON file containing ground truth relevance judgments')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--k-values', nargs='+', type=int, default=[1, 3, 5, 10], 
                       help='K values for precision@k, recall@k, NDCG@k evaluation')
    parser.add_argument('--extensions', nargs='+', default=['.txt', '.md', '.markdown'], 
                       help='File extensions to include from corpus')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        # Load data
        print("Loading evaluation data...")
        queries = load_queries(args.queries)
        ground_truth = load_ground_truth(args.ground_truth)
        documents = load_corpus(args.corpus, args.extensions)
        
        print(f"Loaded {len(queries)} queries, {len(documents)} documents, ground truth for {len(ground_truth)} queries")
        
        # Build retrieval system
        retriever = TFIDFRetriever(documents)
        
        # Run evaluation
        evaluator = RetrievalEvaluator()
        results = evaluator.evaluate(queries, ground_truth, retriever, args.k_values)
        
        # Generate recommendations
        recommendations = generate_recommendations(results)
        results['recommendations'] = recommendations
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        
        # Print summary
        print("\n" + results['evaluation_summary'])
        
        print("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        if args.verbose:
            print(f"\nDetailed Metrics:")
            for metric, value in results['aggregate_metrics'].items():
                print(f"  {metric}: {value:.4f}")
            
            print(f"\nFailure Analysis:")
            fa = results['failure_analysis']
            print(f"  Poor precision queries: {fa['poor_precision_count']}")
            print(f"  Poor recall queries: {fa['poor_recall_count']}")
            print(f"  Zero result queries: {fa['zero_results_count']}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0
