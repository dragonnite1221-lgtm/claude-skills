# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chunking_optimizer_base import *  # noqa: F403,E402
# fmt: off
from chunking_optimizer_p1 import ChunkingStrategy, DocumentCorpus, FixedSizeChunker  # noqa: E402,E501
from chunking_optimizer_p2 import ParagraphChunker, SentenceChunker  # noqa: E402,E501
from chunking_optimizer_p3 import SemanticChunker  # noqa: E402,E501
from chunking_optimizer_p4 import ChunkAnalyzer  # noqa: E402,E501
# fmt: on


class ChunkingOptimizer:
    """Main optimizer that tests different chunking strategies."""
    
    def __init__(self):
        self.analyzer = ChunkAnalyzer()
    
    def optimize(self, corpus: DocumentCorpus, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test all chunking strategies and recommend the best one."""
        config = config or {}
        
        strategies = self._create_strategies(config)
        results = {}
        
        print(f"Testing {len(strategies)} chunking strategies...")
        
        for strategy in strategies:
            print(f"  Testing {strategy.name}...")
            strategy_results = self._test_strategy(corpus, strategy)
            results[strategy.name] = strategy_results
        
        # Recommend best strategy
        recommendation = self._recommend_strategy(results)
        
        return {
            'corpus_info': {
                'document_count': len(corpus.documents),
                'total_size': sum(d['size'] for d in corpus.documents),
                'avg_document_size': statistics.mean([d['size'] for d in corpus.documents])
            },
            'strategy_results': results,
            'recommendation': recommendation,
            'sample_chunks': self._generate_sample_chunks(corpus, recommendation['best_strategy'])
        }
    
    def _create_strategies(self, config: Dict[str, Any]) -> List[ChunkingStrategy]:
        """Create all chunking strategies to test."""
        strategies = []
        
        # Fixed-size strategies
        for size in config.get('fixed_sizes', [512, 1000, 1500]):
            for overlap in config.get('overlaps', [50, 100]):
                strategies.append(FixedSizeChunker(size, overlap, 'char'))
        
        # Sentence-based strategies
        for max_size in config.get('sentence_max_sizes', [800, 1200]):
            strategies.append(SentenceChunker(max_size))
        
        # Paragraph-based strategies
        for max_size in config.get('paragraph_max_sizes', [1500, 2000]):
            strategies.append(ParagraphChunker(max_size))
        
        # Semantic strategies
        for max_size in config.get('semantic_max_sizes', [1200, 1800]):
            strategies.append(SemanticChunker(max_size))
        
        return strategies
    
    def _test_strategy(self, corpus: DocumentCorpus, strategy: ChunkingStrategy) -> Dict[str, Any]:
        """Test a single chunking strategy."""
        all_chunks = []
        document_results = []
        
        for doc in corpus.documents:
            try:
                chunks = strategy.chunk(doc['content'])
                all_chunks.extend(chunks)
                
                doc_analysis = self.analyzer.analyze_chunks(chunks)
                document_results.append({
                    'path': doc['path'],
                    'chunk_count': len(chunks),
                    'analysis': doc_analysis
                })
            except Exception as e:
                print(f"    Error processing {doc['path']}: {e}")
                continue
        
        # Overall analysis
        overall_analysis = self.analyzer.analyze_chunks(all_chunks)
        
        return {
            'strategy_config': strategy.config,
            'total_chunks': len(all_chunks),
            'overall_analysis': overall_analysis,
            'document_results': document_results,
            'performance_score': self._calculate_performance_score(overall_analysis)
        }
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score for a strategy."""
        if 'error' in analysis:
            return 0.0
        
        size_stats = analysis['size_statistics']
        boundary_quality = analysis['boundary_quality']
        coherence = analysis['semantic_coherence']
        
        # Normalize metrics to 0-1 range and combine
        size_consistency = 1.0 - min(size_stats['std'] / size_stats['mean'], 1.0) if size_stats['mean'] > 0 else 0
        boundary_score = (boundary_quality['sentence_boundary_ratio'] + boundary_quality['word_boundary_ratio']) / 2
        coherence_score = coherence
        
        # Weighted combination
        return (size_consistency * 0.3 + boundary_score * 0.4 + coherence_score * 0.3)
    
    def _recommend_strategy(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend the best chunking strategy based on analysis."""
        best_strategy = None
        best_score = 0
        
        strategy_scores = {}
        
        for strategy_name, result in results.items():
            score = result['performance_score']
            strategy_scores[strategy_name] = score
            
            if score > best_score:
                best_score = score
                best_strategy = strategy_name
        
        return {
            'best_strategy': best_strategy,
            'best_score': best_score,
            'all_scores': strategy_scores,
            'reasoning': self._generate_reasoning(best_strategy, results[best_strategy] if best_strategy else None)
        }
    
    def _generate_reasoning(self, strategy_name: str, result: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for the recommendation."""
        if not result:
            return "No valid strategy found."
        
        analysis = result['overall_analysis']
        size_stats = analysis['size_statistics']
        boundary = analysis['boundary_quality']
        
        reasoning = f"Recommended '{strategy_name}' because:\n"
        reasoning += f"- Average chunk size: {size_stats['mean']:.0f} characters\n"
        reasoning += f"- Size consistency: {size_stats['std']:.0f} std deviation\n"
        reasoning += f"- Boundary quality: {boundary['sentence_boundary_ratio']:.2%} clean sentence breaks\n"
        reasoning += f"- Semantic coherence: {analysis['semantic_coherence']:.3f}\n"
        
        return reasoning
    
    def _generate_sample_chunks(self, corpus: DocumentCorpus, strategy_name: str) -> List[Dict[str, Any]]:
        """Generate sample chunks using the recommended strategy."""
        if not strategy_name or not corpus.documents:
            return []
        
        # Create strategy instance
        strategy = None
        if 'fixed_size' in strategy_name:
            strategy = FixedSizeChunker()
        elif 'sentence' in strategy_name:
            strategy = SentenceChunker()
        elif 'paragraph' in strategy_name:
            strategy = ParagraphChunker()
        elif 'semantic' in strategy_name:
            strategy = SemanticChunker()
        
        if not strategy:
            return []
        
        # Get chunks from first document
        sample_doc = corpus.documents[0]
        chunks = strategy.chunk(sample_doc['content'])
        
        # Return first 3 chunks as samples
        return chunks[:3]
