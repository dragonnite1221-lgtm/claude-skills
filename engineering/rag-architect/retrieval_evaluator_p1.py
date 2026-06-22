# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from retrieval_evaluator_base import *  # noqa: F403,E402
from retrieval_evaluator_p0 import Document  # noqa: F401,E501


class TFIDFRetriever:
    """TF-IDF based retrieval system - no external dependencies."""
    
    def __init__(self, documents: List[Document]):
        self.documents = {doc.doc_id: doc for doc in documents}
        self.doc_ids = list(self.documents.keys())
        self.vocabulary = set()
        self.tf_scores = {}  # doc_id -> {term: tf_score}
        self.df_scores = {}  # term -> document_frequency
        self.idf_scores = {}  # term -> idf_score
        self._build_index()
    
    def _build_index(self):
        """Build TF-IDF index from documents."""
        print(f"Building TF-IDF index for {len(self.documents)} documents...")
        
        # Calculate term frequencies and build vocabulary
        for doc_id, doc in self.documents.items():
            term_counts = Counter(doc.tokens)
            doc_length = len(doc.tokens)
            
            # Calculate TF scores (term_count / doc_length)
            tf_scores = {}
            for term, count in term_counts.items():
                tf_scores[term] = count / doc_length if doc_length > 0 else 0
                self.vocabulary.add(term)
            
            self.tf_scores[doc_id] = tf_scores
        
        # Calculate document frequencies
        for term in self.vocabulary:
            df = sum(1 for doc in self.documents.values() if term in doc.tokens)
            self.df_scores[term] = df
        
        # Calculate IDF scores: log(N / df)
        num_docs = len(self.documents)
        for term, df in self.df_scores.items():
            self.idf_scores[term] = math.log(num_docs / df) if df > 0 else 0
    
    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """Search for documents matching the query using TF-IDF similarity."""
        query_tokens = re.findall(r'\b[a-zA-Z0-9]+\b', query.lower())
        if not query_tokens:
            return []
        
        # Calculate query TF scores
        query_tf = Counter(query_tokens)
        query_length = len(query_tokens)
        
        # Calculate TF-IDF similarity for each document
        scores = {}
        for doc_id in self.doc_ids:
            score = self._calculate_similarity(query_tf, query_length, doc_id)
            if score > 0:
                scores[doc_id] = score
        
        # Sort by score and return top k
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:k]
    
    def _calculate_similarity(self, query_tf: Counter, query_length: int, doc_id: str) -> float:
        """Calculate cosine similarity between query and document using TF-IDF."""
        doc_tf = self.tf_scores[doc_id]
        
        # Calculate TF-IDF vectors
        query_vector = []
        doc_vector = []
        
        # Only consider terms that appear in both query and document
        common_terms = set(query_tf.keys()) & set(doc_tf.keys())
        
        if not common_terms:
            return 0.0
        
        for term in common_terms:
            # Query TF-IDF
            q_tf = query_tf[term] / query_length
            q_tfidf = q_tf * self.idf_scores.get(term, 0)
            query_vector.append(q_tfidf)
            
            # Document TF-IDF
            d_tfidf = doc_tf[term] * self.idf_scores.get(term, 0)
            doc_vector.append(d_tfidf)
        
        # Cosine similarity
        dot_product = sum(q * d for q, d in zip(query_vector, doc_vector))
        query_norm = math.sqrt(sum(q * q for q in query_vector))
        doc_norm = math.sqrt(sum(d * d for d in doc_vector))
        
        if query_norm == 0 or doc_norm == 0:
            return 0.0
        
        return dot_product / (query_norm * doc_norm)


def load_queries(file_path: str) -> List[Dict[str, Any]]:
    """Load queries from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(data, list):
        return data
    elif 'queries' in data:
        return data['queries']
    else:
        raise ValueError("Invalid query file format. Expected list of queries or {'queries': [...]}.")
