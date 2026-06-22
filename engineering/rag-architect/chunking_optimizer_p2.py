# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chunking_optimizer_base import *  # noqa: F403,E402
# fmt: off
from chunking_optimizer_p1 import ChunkingStrategy  # noqa: E402,E501
# fmt: on


class SentenceChunker(ChunkingStrategy):
    """Sentence-based chunking."""
    
    def __init__(self, max_size: int = 1000):
        config = {'max_size': max_size}
        super().__init__('sentence_based', config)
        self.max_size = max_size
        # Simple sentence boundary detection
        self.sentence_endings = re.compile(r'[.!?]+\s+')
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        # Split into sentences
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.max_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'start': 0,  # Approximate
                    'end': len(chunk_text),
                    'size': len(chunk_text),
                    'sentence_count': len(current_chunk)
                })
                chunk_id += 1
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start': 0,
                'end': len(chunk_text),
                'size': len(chunk_text),
                'sentence_count': len(current_chunk)
            })
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting."""
        sentences = []
        parts = self.sentence_endings.split(text)
        
        for i, part in enumerate(parts[:-1]):
            # Add the sentence ending back
            ending_match = list(self.sentence_endings.finditer(text))
            if i < len(ending_match):
                sentence = part + ending_match[i].group().strip()
            else:
                sentence = part
            
            if sentence.strip():
                sentences.append(sentence.strip())
        
        # Add final part if it exists
        if parts[-1].strip():
            sentences.append(parts[-1].strip())
        
        return [s for s in sentences if len(s.strip()) > 0]
class ParagraphChunker(ChunkingStrategy):
    """Paragraph-based chunking."""
    
    def __init__(self, max_size: int = 2000, min_paragraph_size: int = 50):
        config = {'max_size': max_size, 'min_paragraph_size': min_paragraph_size}
        super().__init__('paragraph_based', config)
        self.max_size = max_size
        self.min_paragraph_size = min_paragraph_size
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        # Split by double newlines (paragraph boundaries)
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            # Skip very short paragraphs unless they're the only content
            if paragraph_size < self.min_paragraph_size and len(paragraphs) > 1:
                continue
            
            if current_size + paragraph_size > self.max_size and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'start': 0,
                    'end': len(chunk_text),
                    'size': len(chunk_text),
                    'paragraph_count': len(current_chunk)
                })
                chunk_id += 1
                current_chunk = [paragraph]
                current_size = paragraph_size
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size + 2  # Account for newlines
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start': 0,
                'end': len(chunk_text),
                'size': len(chunk_text),
                'paragraph_count': len(current_chunk)
            })
        
        return chunks
