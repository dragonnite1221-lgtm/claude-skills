# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_evaluator_base import *  # noqa: F403,E402
# fmt: off
from rag_evaluator_p1 import AnswerEvaluation, RetrievalMetrics, calculate_rouge_l, tokenize  # noqa: E402,E501
# fmt: on


def extract_claims(answer: str) -> List[str]:
    """Extract individual claims from an answer"""
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+', answer)
    claims = []

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Filter out very short fragments
            claims.append(sentence)

    return claims
def check_claim_support(claim: str, context: str) -> Tuple[bool, float]:
    """Check if a claim is supported by the context"""
    claim_terms = set(tokenize(claim))
    context_terms = set(tokenize(context))

    if not claim_terms:
        return True, 1.0  # Empty claim is "supported"

    # Check term overlap
    overlap = claim_terms & context_terms
    support_ratio = len(overlap) / len(claim_terms)

    # Also check for ROUGE-L style matching
    rouge_score = calculate_rouge_l(context, claim)

    # Combined support score
    support_score = 0.5 * support_ratio + 0.5 * rouge_score

    return support_score > 0.3, support_score
def evaluate_answer_faithfulness(
    question: str,
    answer: str,
    contexts: List[str],
    question_id: str = ""
) -> AnswerEvaluation:
    """Evaluate if answer is faithful to the provided contexts"""
    claims = extract_claims(answer)
    combined_context = ' '.join(contexts)

    claim_evaluations = []
    supported_claims = 0
    unsupported = []
    context_used = []

    for claim in claims:
        is_supported, score = check_claim_support(claim, combined_context)

        claim_eval = {
            'claim': claim[:100] + '...' if len(claim) > 100 else claim,
            'supported': is_supported,
            'score': round(score, 3)
        }

        # Track which contexts support this claim
        for i, ctx in enumerate(contexts):
            _, ctx_score = check_claim_support(claim, ctx)
            if ctx_score > 0.3:
                claim_eval[f'context_{i}'] = round(ctx_score, 3)
                if f'context_{i}' not in context_used:
                    context_used.append(f'context_{i}')

        claim_evaluations.append(claim_eval)

        if is_supported:
            supported_claims += 1
        else:
            unsupported.append(claim[:100])

    # Faithfulness = % of claims supported
    faithfulness = supported_claims / len(claims) if claims else 1.0

    # Groundedness = average support score
    avg_score = sum(c['score'] for c in claim_evaluations) / len(claim_evaluations) if claim_evaluations else 1.0

    return AnswerEvaluation(
        question_id=question_id,
        faithfulness_score=round(faithfulness, 3),
        groundedness_score=round(avg_score, 3),
        claims=claim_evaluations,
        unsupported_claims=unsupported,
        context_used=context_used
    )
def calculate_retrieval_metrics(
    retrieved: List[str],
    relevant: Set[str],
    k: int = 5
) -> RetrievalMetrics:
    """Calculate standard retrieval metrics"""
    retrieved_k = retrieved[:k]

    # Precision@K
    relevant_in_k = sum(1 for doc in retrieved_k if doc in relevant)
    precision = relevant_in_k / k if k > 0 else 0

    # Recall@K
    recall = relevant_in_k / len(relevant) if relevant else 0

    # MRR (Mean Reciprocal Rank)
    mrr = 0.0
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            mrr = 1.0 / (i + 1)
            break

    # NDCG@K
    dcg = 0.0
    for i, doc in enumerate(retrieved_k):
        rel = 1 if doc in relevant else 0
        dcg += rel / math.log2(i + 2)

    # Ideal DCG (all relevant at top)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), k)))
    ndcg = dcg / idcg if idcg > 0 else 0

    return RetrievalMetrics(
        precision_at_k=round(precision, 3),
        recall_at_k=round(recall, 3),
        mrr=round(mrr, 3),
        ndcg_at_k=round(ndcg, 3),
        k=k
    )
