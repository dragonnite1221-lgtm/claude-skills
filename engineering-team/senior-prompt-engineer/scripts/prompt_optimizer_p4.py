# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prompt_optimizer_base import *  # noqa: F403,E402
# fmt: off
from prompt_optimizer_p1 import estimate_cost, estimate_tokens  # noqa: E402,E501
from prompt_optimizer_p2 import extract_few_shot_examples  # noqa: E402,E501
from prompt_optimizer_p3 import analyze_prompt, format_report, optimize_prompt  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Optimizer - Analyze and optimize prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s prompt.txt --analyze
  %(prog)s prompt.txt --tokens --model claude-3-sonnet
  %(prog)s prompt.txt --optimize --output optimized.txt
  %(prog)s prompt.txt --extract-examples --output examples.json
        """
    )

    parser.add_argument('prompt', help='Prompt file to analyze')
    parser.add_argument('--analyze', '-a', action='store_true', help='Run full analysis')
    parser.add_argument('--tokens', '-t', action='store_true', help='Count tokens only')
    parser.add_argument('--optimize', '-O', action='store_true', help='Generate optimized version')
    parser.add_argument('--extract-examples', '-e', action='store_true', help='Extract few-shot examples')
    parser.add_argument('--model', '-m', default='gpt-4',
                       choices=['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                       help='Model for token/cost estimation')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--compare', '-c', help='Compare with baseline analysis JSON')

    args = parser.parse_args()

    # Read prompt file
    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        print(f"Error: File not found: {args.prompt}", file=sys.stderr)
        sys.exit(1)

    text = prompt_path.read_text(encoding='utf-8')

    # Tokens only
    if args.tokens:
        token_count = estimate_tokens(text, args.model)
        cost = estimate_cost(token_count, args.model)
        if args.json:
            print(json.dumps({
                'tokens': token_count,
                'cost': cost,
                'model': args.model
            }, indent=2))
        else:
            print(f"Tokens: {token_count:,}")
            print(f"Estimated cost: ${cost:.4f} ({args.model})")
        sys.exit(0)

    # Extract examples
    if args.extract_examples:
        examples = extract_few_shot_examples(text)
        output = [asdict(ex) for ex in examples]

        if args.output:
            Path(args.output).write_text(json.dumps(output, indent=2))
            print(f"Extracted {len(examples)} examples to {args.output}")
        else:
            print(json.dumps(output, indent=2))
        sys.exit(0)

    # Optimize
    if args.optimize:
        optimized = optimize_prompt(text)

        if args.output:
            Path(args.output).write_text(optimized)
            print(f"Optimized prompt written to {args.output}")

            # Show comparison
            orig_tokens = estimate_tokens(text, args.model)
            new_tokens = estimate_tokens(optimized, args.model)
            saved = orig_tokens - new_tokens
            print(f"Tokens: {orig_tokens:,} -> {new_tokens:,} (saved {saved:,})")
        else:
            print(optimized)
        sys.exit(0)

    # Default: full analysis
    analysis = analyze_prompt(text, args.model)

    # Compare with baseline
    if args.compare:
        baseline_path = Path(args.compare)
        if baseline_path.exists():
            baseline = json.loads(baseline_path.read_text())
            print("\n📊 COMPARISON WITH BASELINE")
            print(f"  Tokens: {baseline.get('token_count', 0):,} -> {analysis.token_count:,}")
            print(f"  Clarity: {baseline.get('clarity_score', 0)} -> {analysis.clarity_score}")
            print(f"  Issues: {len(baseline.get('issues', []))} -> {len(analysis.issues)}")
            print()

    if args.json:
        print(json.dumps(asdict(analysis), indent=2))
    else:
        print(format_report(analysis))

    # Write to output file
    if args.output:
        output_data = asdict(analysis)
        Path(args.output).write_text(json.dumps(output_data, indent=2))
        print(f"\nAnalysis saved to {args.output}")
