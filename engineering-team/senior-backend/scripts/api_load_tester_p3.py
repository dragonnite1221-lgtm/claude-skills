# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_load_tester_base import *  # noqa: F403,E402
# fmt: off
from api_load_tester_p1 import LoadTestResults  # noqa: E402,E501
# fmt: on


def print_results(results: LoadTestResults, verbose: bool = False):
    """Print formatted load test results."""
    print("\n" + "=" * 60)
    print("LOAD TEST RESULTS")
    print("=" * 60)

    print(f"\nTarget: {results.target_url}")
    print(f"Method: {results.method}")
    print(f"Duration: {results.duration_seconds:.1f}s")
    print(f"Concurrency: {results.concurrency}")

    print(f"\nTHROUGHPUT:")
    print(f"  Total requests: {results.total_requests:,}")
    print(f"  Requests/sec: {results.requests_per_second:.1f}")
    print(f"  Successful: {results.successful_requests:,} ({results.success_rate():.1f}%)")
    print(f"  Failed: {results.failed_requests:,}")

    print(f"\nLATENCY (ms):")
    print(f"  Min: {results.latency_min:.1f}")
    print(f"  Avg: {results.latency_avg:.1f}")
    print(f"  P50: {results.latency_p50:.1f}")
    print(f"  P90: {results.latency_p90:.1f}")
    print(f"  P95: {results.latency_p95:.1f}")
    print(f"  P99: {results.latency_p99:.1f}")
    print(f"  Max: {results.latency_max:.1f}")
    print(f"  StdDev: {results.latency_stddev:.1f}")

    if results.errors_by_type:
        print(f"\nERRORS:")
        for error_type, count in sorted(results.errors_by_type.items(), key=lambda x: -x[1]):
            print(f"  {error_type}: {count}")

    if verbose:
        print(f"\nTRANSFER:")
        print(f"  Total bytes: {results.total_bytes_received:,}")
        print(f"  Throughput: {results.throughput_mbps:.2f} Mbps")

    # Recommendations
    print(f"\nRECOMMENDATIONS:")

    if results.latency_p99 > 500:
        print(f"  Warning: P99 latency ({results.latency_p99:.0f}ms) exceeds 500ms")
        print(f"    Consider: Connection pooling, query optimization, caching")

    if results.latency_p95 > 200:
        print(f"  Warning: P95 latency ({results.latency_p95:.0f}ms) exceeds 200ms target")

    if results.success_rate() < 99.0:
        print(f"  Warning: Success rate ({results.success_rate():.1f}%) below 99%")
        print(f"    Check server capacity and error logs")

    if results.latency_stddev > results.latency_avg:
        print(f"  Warning: High latency variance (stddev > avg)")
        print(f"    Indicates inconsistent performance")

    if results.success_rate() >= 99.0 and results.latency_p95 <= 200:
        print(f"  Performance looks good for this load level")

    print("=" * 60)
def compare_results(results1: LoadTestResults, results2: LoadTestResults):
    """Compare two load test results."""
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)

    print(f"\n{'Metric':<25} {'Endpoint 1':<15} {'Endpoint 2':<15} {'Diff':<15}")
    print("-" * 70)

    # Helper to format diff
    def diff_str(v1: float, v2: float, lower_better: bool = True) -> str:
        if v1 == 0:
            return "N/A"
        diff_pct = ((v2 - v1) / v1) * 100
        symbol = "-" if (diff_pct < 0) == lower_better else "+"
        color_good = diff_pct < 0 if lower_better else diff_pct > 0
        return f"{symbol}{abs(diff_pct):.1f}%"

    metrics = [
        ("Requests/sec", results1.requests_per_second, results2.requests_per_second, False),
        ("Success rate (%)", results1.success_rate(), results2.success_rate(), False),
        ("Latency Avg (ms)", results1.latency_avg, results2.latency_avg, True),
        ("Latency P50 (ms)", results1.latency_p50, results2.latency_p50, True),
        ("Latency P90 (ms)", results1.latency_p90, results2.latency_p90, True),
        ("Latency P95 (ms)", results1.latency_p95, results2.latency_p95, True),
        ("Latency P99 (ms)", results1.latency_p99, results2.latency_p99, True),
    ]

    for name, v1, v2, lower_better in metrics:
        print(f"{name:<25} {v1:<15.1f} {v2:<15.1f} {diff_str(v1, v2, lower_better):<15}")

    print("-" * 70)

    # Summary
    print(f"\nEndpoint 1: {results1.target_url}")
    print(f"Endpoint 2: {results2.target_url}")

    # Determine winner
    score1, score2 = 0, 0

    if results1.requests_per_second > results2.requests_per_second:
        score1 += 1
    else:
        score2 += 1

    if results1.latency_p95 < results2.latency_p95:
        score1 += 1
    else:
        score2 += 1

    if results1.success_rate() > results2.success_rate():
        score1 += 1
    else:
        score2 += 1

    print(f"\nOverall: {'Endpoint 1' if score1 > score2 else 'Endpoint 2'} performs better")

    print("=" * 60)
