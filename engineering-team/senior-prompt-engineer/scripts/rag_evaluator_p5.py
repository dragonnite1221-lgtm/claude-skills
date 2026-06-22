# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from rag_evaluator_base import *  # noqa: F403,E402
# fmt: off
from rag_evaluator_p1 import RAGEvaluationReport  # noqa: E402,E501
from rag_evaluator_p4 import evaluate_rag_system  # noqa: E402,E501
# fmt: on


def format_report(report: RAGEvaluationReport) -> str:
    """Format report as human-readable text"""
    lines = []
    lines.append("=" * 60)
    lines.append("RAG EVALUATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"📊 SUMMARY")
    lines.append(f"  Questions evaluated: {report.total_questions}")
    lines.append(f"  Coverage: {report.coverage:.1%}")
    lines.append("")

    lines.append("📈 RETRIEVAL METRICS")
    lines.append(f"  Context Relevance:    {report.avg_context_relevance:.2f} {'✅' if report.avg_context_relevance >= 0.8 else '⚠️'} (target: >0.80)")
    lines.append(f"  Precision@{report.retrieval_metrics.get('k', 5)}:         {report.retrieval_metrics.get('precision_at_k', 0):.2f}")
    lines.append("")

    lines.append("📝 GENERATION METRICS")
    lines.append(f"  Answer Faithfulness:  {report.avg_faithfulness:.2f} {'✅' if report.avg_faithfulness >= 0.95 else '⚠️'} (target: >0.95)")
    lines.append(f"  Groundedness:         {report.avg_groundedness:.2f} {'✅' if report.avg_groundedness >= 0.85 else '⚠️'} (target: >0.85)")
    lines.append("")

    if report.issues:
        lines.append(f"⚠️ ISSUES FOUND ({len(report.issues)})")
        for issue in report.issues[:10]:
            if issue['type'] == 'unsupported_claim':
                lines.append(f"  Q{issue['question_id']}: {len(issue.get('claims', []))} unsupported claim(s)")
            elif issue['type'] == 'low_relevance':
                lines.append(f"  Q{issue['question_id']}: Low relevance contexts: {issue.get('contexts', [])}")
        if len(report.issues) > 10:
            lines.append(f"  ... and {len(report.issues) - 10} more issues")
        lines.append("")

    lines.append("💡 RECOMMENDATIONS")
    for i, rec in enumerate(report.recommendations, 1):
        lines.append(f"  {i}. {rec}")
    lines.append("")

    lines.append("=" * 60)

    return '\n'.join(lines)
def main():
    parser = argparse.ArgumentParser(
        description="RAG Evaluator - Evaluate Retrieval-Augmented Generation systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --contexts contexts.json --questions questions.json
  %(prog)s --contexts ctx.json --questions q.json --k 10
  %(prog)s --contexts ctx.json --questions q.json --output report.json --verbose

Input file formats:

questions.json:
[
  {"id": "q1", "question": "What is X?", "answer": "X is..."},
  {"id": "q2", "question": "How does Y work?", "answer": "Y works by..."}
]

contexts.json:
[
  {"question_id": "q1", "content": "Retrieved context text..."},
  {"question_id": "q2", "content": "Another context..."}
]
        """
    )

    parser.add_argument('--contexts', '-c', required=True, help='JSON file with retrieved contexts')
    parser.add_argument('--questions', '-q', required=True, help='JSON file with questions and answers')
    parser.add_argument('--k', type=int, default=5, help='Number of top contexts to evaluate (default: 5)')
    parser.add_argument('--output', '-o', help='Output file for detailed report (JSON)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON instead of text')
    parser.add_argument('--verbose', '-v', action='store_true', help='Include per-question details')
    parser.add_argument('--compare', help='Compare with baseline report JSON')

    args = parser.parse_args()

    # Load input files
    contexts_path = Path(args.contexts)
    questions_path = Path(args.questions)

    if not contexts_path.exists():
        print(f"Error: Contexts file not found: {args.contexts}", file=sys.stderr)
        sys.exit(1)

    if not questions_path.exists():
        print(f"Error: Questions file not found: {args.questions}", file=sys.stderr)
        sys.exit(1)

    try:
        contexts = json.loads(contexts_path.read_text(encoding='utf-8'))
        questions = json.loads(questions_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}", file=sys.stderr)
        sys.exit(1)

    # Run evaluation
    report = evaluate_rag_system(questions, contexts, k=args.k, verbose=args.verbose)

    # Compare with baseline
    if args.compare:
        baseline_path = Path(args.compare)
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text())
            print("\n📊 COMPARISON WITH BASELINE")
            print(f"  Relevance:    {baseline.get('avg_context_relevance', 0):.2f} -> {report.avg_context_relevance:.2f}")
            print(f"  Faithfulness: {baseline.get('avg_faithfulness', 0):.2f} -> {report.avg_faithfulness:.2f}")
            print(f"  Groundedness: {baseline.get('avg_groundedness', 0):.2f} -> {report.avg_groundedness:.2f}")
            print()

    # Output
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(format_report(report))

    # Save to file
    if args.output:
        Path(args.output).write_text(json.dumps(asdict(report), indent=2))
        print(f"\nDetailed report saved to {args.output}")
