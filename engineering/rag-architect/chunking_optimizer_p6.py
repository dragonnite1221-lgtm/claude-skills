# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chunking_optimizer_base import *  # noqa: F403,E402
# fmt: off
from chunking_optimizer_p1 import DocumentCorpus  # noqa: E402,E501
from chunking_optimizer_p5 import ChunkingOptimizer  # noqa: E402,E501
# fmt: on


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='Analyze documents and recommend optimal chunking strategy')
    parser.add_argument('directory', help='Directory containing text/markdown documents')
    parser.add_argument('--output', '-o', help='Output file for results (JSON format)')
    parser.add_argument('--config', '-c', help='Configuration file (JSON format)')
    parser.add_argument('--extensions', nargs='+', default=['.txt', '.md', '.markdown'], 
                       help='File extensions to process')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    try:
        # Load corpus
        print(f"Loading documents from {args.directory}...")
        corpus = DocumentCorpus(args.directory, args.extensions)
        
        # Run optimization
        optimizer = ChunkingOptimizer()
        results = optimizer.optimize(corpus, config)
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        
        # Print summary
        print("\n" + "="*60)
        print("CHUNKING OPTIMIZATION RESULTS")
        print("="*60)
        
        corpus_info = results['corpus_info']
        print(f"Corpus: {corpus_info['document_count']} documents, {corpus_info['total_size']:,} characters")
        
        recommendation = results['recommendation']
        print(f"\nRecommended Strategy: {recommendation['best_strategy']}")
        print(f"Performance Score: {recommendation['best_score']:.3f}")
        print(f"\nReasoning:\n{recommendation['reasoning']}")
        
        if args.verbose:
            print("\nAll Strategy Scores:")
            for strategy, score in recommendation['all_scores'].items():
                print(f"  {strategy}: {score:.3f}")
        
        print("\nSample Chunks:")
        for i, chunk in enumerate(results['sample_chunks'][:2]):
            print(f"\nChunk {i+1} ({chunk['size']} chars):")
            print("-" * 40)
            print(chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'])
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0
