# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and optimize vision model inference"
    )
    parser.add_argument('model_path', help='Path to model file')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze model structure')
    parser.add_argument('--benchmark', action='store_true',
                       help='Benchmark inference speed')
    parser.add_argument('--input-size', type=int, nargs=2, default=[640, 640],
                       metavar=('H', 'W'), help='Input image size')
    parser.add_argument('--batch-sizes', type=int, nargs='+', default=[1, 4, 8],
                       help='Batch sizes to benchmark')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of benchmark iterations')
    parser.add_argument('--warmup', type=int, default=10,
                       help='Number of warmup iterations')
    parser.add_argument('--target', choices=['gpu', 'cpu', 'edge', 'mobile', 'apple', 'intel'],
                       default='gpu', help='Target deployment platform')
    parser.add_argument('--recommend', action='store_true',
                       help='Show optimization recommendations')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    parser.add_argument('--output', '-o', help='Output file path')

    args = parser.parse_args()

    if not Path(args.model_path).exists():
        logger.error(f"Model not found: {args.model_path}")
        sys.exit(1)

    try:
        optimizer = InferenceOptimizer(args.model_path)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    results = {}

    # Analyze model
    if args.analyze or not (args.benchmark or args.recommend):
        results['analysis'] = optimizer.analyze_model()

    # Benchmark
    if args.benchmark:
        results['benchmark'] = optimizer.benchmark(
            input_size=tuple(args.input_size),
            batch_sizes=args.batch_sizes,
            num_iterations=args.iterations,
            warmup=args.warmup
        )

    # Recommendations
    if args.recommend:
        if not optimizer.model_info:
            optimizer.analyze_model()
        results['recommendations'] = optimizer.get_optimization_recommendations(args.target)

    # Output
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        optimizer.print_summary()

        if args.recommend and 'recommendations' in results:
            print("OPTIMIZATION RECOMMENDATIONS")
            print("-" * 70)
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"\n{i}. {rec['step'].upper()}")
                print(f"   {rec['description']}")
                print(f"   Expected speedup: {rec['expected_speedup']}")
                if rec.get('command'):
                    print(f"   Command: {rec['command']}")
            print()

    # Save to file
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {args.output}")
