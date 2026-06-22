# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402


class Document:
    """Represents a document in the corpus."""
    
    def __init__(self, doc_id: str, title: str, content: str, path: str = ""):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.path = path
        self.tokens = self._tokenize(content)
        self.token_count = len(self.tokens)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization - split on whitespace and punctuation."""
        # Convert to lowercase and extract words
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        return tokens
    
    def __str__(self):
        return f"Document({self.doc_id}, '{self.title[:50]}...', {self.token_count} tokens)"
