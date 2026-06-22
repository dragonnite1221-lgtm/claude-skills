# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chunking_optimizer_base import *  # noqa: F403,E402


class ChunkAnalyzer:
    """Analyzes chunks and provides quality metrics."""
    
    def __init__(self):
        self.vocabulary = set()
        self.word_freq = Counter()
    
    def analyze_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive chunk analysis."""
        if not chunks:
            return {'error': 'No chunks to analyze'}
        
        sizes = [chunk['size'] for chunk in chunks]
        
        # Basic size statistics
        size_stats = {
            'count': len(chunks),
            'mean': statistics.mean(sizes),
            'median': statistics.median(sizes),
            'std': statistics.stdev(sizes) if len(sizes) > 1 else 0,
            'min': min(sizes),
            'max': max(sizes),
            'total': sum(sizes)
        }
        
        # Boundary quality analysis
        boundary_quality = self._analyze_boundary_quality(chunks)
        
        # Semantic coherence (simple heuristic)
        coherence_score = self._calculate_semantic_coherence(chunks)
        
        # Vocabulary distribution
        vocab_stats = self._analyze_vocabulary(chunks)
        
        return {
            'size_statistics': size_stats,
            'boundary_quality': boundary_quality,
            'semantic_coherence': coherence_score,
            'vocabulary_statistics': vocab_stats
        }
    
    def _analyze_boundary_quality(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well chunks respect natural boundaries."""
        sentence_breaks = 0
        word_breaks = 0
        total_chunks = len(chunks)
        
        sentence_endings = re.compile(r'[.!?]\s*$')
        
        for chunk in chunks:
            text = chunk['text'].strip()
            if not text:
                continue
            
            # Check if chunk ends with sentence boundary
            if sentence_endings.search(text):
                sentence_breaks += 1
            
            # Check if chunk ends with word boundary
            if text[-1].isalnum() or text[-1] in '.!?':
                word_breaks += 1
        
        return {
            'sentence_boundary_ratio': sentence_breaks / total_chunks if total_chunks > 0 else 0,
            'word_boundary_ratio': word_breaks / total_chunks if total_chunks > 0 else 0,
            'clean_breaks': sentence_breaks,
            'total_chunks': total_chunks
        }
    
    def _calculate_semantic_coherence(self, chunks: List[Dict[str, Any]]) -> float:
        """Simple semantic coherence heuristic based on vocabulary overlap."""
        if len(chunks) < 2:
            return 1.0
        
        coherence_scores = []
        
        for i in range(len(chunks) - 1):
            chunk1_words = set(re.findall(r'\b\w+\b', chunks[i]['text'].lower()))
            chunk2_words = set(re.findall(r'\b\w+\b', chunks[i+1]['text'].lower()))
            
            if not chunk1_words or not chunk2_words:
                continue
            
            # Jaccard similarity as coherence measure
            intersection = len(chunk1_words & chunk2_words)
            union = len(chunk1_words | chunk2_words)
            
            if union > 0:
                coherence_scores.append(intersection / union)
        
        return statistics.mean(coherence_scores) if coherence_scores else 0.0
    
    def _analyze_vocabulary(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze vocabulary distribution across chunks."""
        all_words = []
        chunk_vocab_sizes = []
        
        for chunk in chunks:
            words = re.findall(r'\b\w+\b', chunk['text'].lower())
            all_words.extend(words)
            chunk_vocab_sizes.append(len(set(words)))
        
        total_vocab = len(set(all_words))
        word_freq = Counter(all_words)
        
        return {
            'total_vocabulary': total_vocab,
            'avg_chunk_vocabulary': statistics.mean(chunk_vocab_sizes) if chunk_vocab_sizes else 0,
            'vocabulary_diversity': total_vocab / len(all_words) if all_words else 0,
            'most_common_words': word_freq.most_common(10)
        }
