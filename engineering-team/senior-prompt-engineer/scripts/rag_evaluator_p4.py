# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_evaluator_base import *  # noqa: F403,E402
# fmt: off
from rag_evaluator_p1 import RAGEvaluationReport, evaluate_context_relevance  # noqa: E402,E501
from rag_evaluator_p2 import evaluate_answer_faithfulness  # noqa: E402,E501
from rag_evaluator_p3 import generate_recommendations  # noqa: E402,E501
# fmt: on


def evaluate_rag_system(
    questions: List[Dict],
    contexts: List[Dict],
    k: int = 5,
    verbose: bool = False
) -> RAGEvaluationReport:
    """Comprehensive RAG system evaluation"""

    all_context_scores = []
    all_faithfulness_scores = []
    all_groundedness_scores = []
    issues = []
    question_details = []

    questions_with_context = 0

    for q_data in questions:
        question = q_data.get('question', q_data.get('query', ''))
        question_id = q_data.get('id', str(questions.index(q_data)))
        answer = q_data.get('answer', q_data.get('response', ''))
        expected = q_data.get('expected', q_data.get('ground_truth', ''))

        # Find contexts for this question
        q_contexts = []
        for ctx in contexts:
            if ctx.get('question_id') == question_id or ctx.get('query_id') == question_id:
                q_contexts.append(ctx.get('content', ctx.get('text', '')))

        # If no specific contexts, use all contexts (for simple datasets)
        if not q_contexts:
            q_contexts = [ctx.get('content', ctx.get('text', ''))
                        for ctx in contexts[:k]]

        if q_contexts:
            questions_with_context += 1

        # Evaluate context relevance
        context_evals = []
        for i, ctx in enumerate(q_contexts[:k]):
            eval_result = evaluate_context_relevance(question, ctx, f"ctx_{i}")
            context_evals.append(eval_result)
            all_context_scores.append(eval_result.relevance_score)

        # Evaluate answer faithfulness
        if answer and q_contexts:
            answer_eval = evaluate_answer_faithfulness(question, answer, q_contexts, question_id)
            all_faithfulness_scores.append(answer_eval.faithfulness_score)
            all_groundedness_scores.append(answer_eval.groundedness_score)

            # Track issues
            if answer_eval.unsupported_claims:
                issues.append({
                    'type': 'unsupported_claim',
                    'question_id': question_id,
                    'claims': answer_eval.unsupported_claims[:3]
                })

        # Check for low relevance contexts
        low_relevance = [e for e in context_evals if e.relevance_score < 0.5]
        if low_relevance:
            issues.append({
                'type': 'low_relevance',
                'question_id': question_id,
                'contexts': [e.context_id for e in low_relevance]
            })

        if verbose:
            question_details.append({
                'question_id': question_id,
                'question': question[:100],
                'context_scores': [asdict(e) for e in context_evals],
                'answer_faithfulness': all_faithfulness_scores[-1] if all_faithfulness_scores else None
            })

    # Calculate aggregates
    avg_context_relevance = sum(all_context_scores) / len(all_context_scores) if all_context_scores else 0
    avg_faithfulness = sum(all_faithfulness_scores) / len(all_faithfulness_scores) if all_faithfulness_scores else 0
    avg_groundedness = sum(all_groundedness_scores) / len(all_groundedness_scores) if all_groundedness_scores else 0
    coverage = questions_with_context / len(questions) if questions else 0

    # Simulated retrieval metrics (based on relevance scores)
    high_relevance = sum(1 for s in all_context_scores if s > 0.5)
    retrieval_metrics = {
        'precision_at_k': round(high_relevance / len(all_context_scores) if all_context_scores else 0, 3),
        'estimated_recall': round(coverage, 3),
        'k': k
    }

    report = RAGEvaluationReport(
        total_questions=len(questions),
        avg_context_relevance=round(avg_context_relevance, 3),
        avg_faithfulness=round(avg_faithfulness, 3),
        avg_groundedness=round(avg_groundedness, 3),
        retrieval_metrics=retrieval_metrics,
        coverage=round(coverage, 3),
        issues=issues[:20],  # Limit to 20 issues
        recommendations=[],
        question_details=question_details if verbose else []
    )

    report.recommendations = generate_recommendations(report)

    return report
