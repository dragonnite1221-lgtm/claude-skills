# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from chunking_optimizer_base import *  # noqa: F403,E402


class DocumentCorpus:
    """Handles loading and preprocessing of document corpus."""
    
    def __init__(self, directory: str, extensions: List[str] = None):
        self.directory = Path(directory)
        self.extensions = extensions or ['.txt', '.md', '.markdown']
        self.documents = []
        self._load_documents()
    
    def _load_documents(self):
        """Load all text documents from directory."""
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory}")
        
        for file_path in self.directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if content.strip():  # Only include non-empty files
                        self.documents.append({
                            'path': str(file_path),
                            'content': content,
                            'size': len(content)
                        })
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
        
        if not self.documents:
            raise ValueError(f"No valid documents found in {self.directory}")
        
        print(f"Loaded {len(self.documents)} documents totaling {sum(d['size'] for d in self.documents):,} characters")
class ChunkingStrategy:
    """Base class for chunking strategies."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks. Returns list of chunk dictionaries."""
        raise NotImplementedError
class FixedSizeChunker(ChunkingStrategy):
    """Fixed-size chunking with optional overlap."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100, unit: str = 'char'):
        config = {'chunk_size': chunk_size, 'overlap': overlap, 'unit': unit}
        super().__init__(f'fixed_size_{unit}', config)
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.unit = unit
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        chunks = []
        if self.unit == 'char':
            return self._chunk_by_chars(text)
        else:  # word-based approximation
            words = text.split()
            return self._chunk_by_words(words)
    
    def _chunk_by_chars(self, text: str) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start': start,
                'end': end,
                'size': len(chunk_text)
            })
            
            start = max(start + self.chunk_size - self.overlap, start + 1)
            chunk_id += 1
            
            if start >= len(text):
                break
        
        return chunks
    
    def _chunk_by_words(self, words: List[str]) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'start': start,
                'end': end,
                'size': len(chunk_text)
            })
            
            start = max(start + self.chunk_size - self.overlap, start + 1)
            chunk_id += 1
            
            if start >= len(words):
                break
        
        return chunks
