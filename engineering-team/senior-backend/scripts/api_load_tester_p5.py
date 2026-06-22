# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_load_tester_base import *  # noqa: F403,E402
# fmt: off
from api_load_tester_p4 import APILoadTester, parse_headers  # noqa: E402,E501
# fmt: on


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='HTTP load testing tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://api.example.com/users --concurrency 50 --duration 30
  %(prog)s https://api.example.com/orders --method POST --body '{"item": 1}'
  %(prog)s https://api.example.com/v1 https://api.example.com/v2 --compare
  %(prog)s https://api.example.com/health --header "Authorization: Bearer token"
        '''
    )

    parser.add_argument(
        'urls',
        nargs='+',
        help='URL(s) to test'
    )
    parser.add_argument(
        '--method', '-m',
        default='GET',
        choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        help='HTTP method (default: GET)'
    )
    parser.add_argument(
        '--body', '-b',
        help='Request body (JSON string)'
    )
    parser.add_argument(
        '--header', '-H',
        action='append',
        dest='headers',
        help='HTTP header (format: "Name: Value")'
    )
    parser.add_argument(
        '--concurrency', '-c',
        type=int,
        default=10,
        help='Number of concurrent requests (default: 10)'
    )
    parser.add_argument(
        '--duration', '-d',
        type=float,
        default=10.0,
        help='Test duration in seconds (default: 10)'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=float,
        default=30.0,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare two endpoints (requires two URLs)'
    )
    parser.add_argument(
        '--no-verify-ssl',
        action='store_true',
        help='Disable SSL certificate verification'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file path for results'
    )

    args = parser.parse_args()

    # Validate
    if args.compare and len(args.urls) < 2:
        print("Error: --compare requires two URLs", file=sys.stderr)
        sys.exit(1)

    # Parse headers
    headers = parse_headers(args.headers)

    try:
        tester = APILoadTester(
            urls=args.urls,
            method=args.method,
            body=args.body,
            headers=headers,
            concurrency=args.concurrency,
            duration=args.duration,
            timeout=args.timeout,
            compare=args.compare,
            verbose=args.verbose,
            verify_ssl=not args.no_verify_ssl,
        )

        results = tester.run()

        if args.json:
            output = json.dumps(results, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"\nResults written to: {args.output}")
            else:
                print(output)
        elif args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults written to: {args.output}")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
