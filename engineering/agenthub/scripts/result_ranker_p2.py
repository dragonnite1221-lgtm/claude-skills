# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from result_ranker_base import *  # noqa: F403,E402


def run_demo():
    """Show demo ranking output."""
    print("=" * 60)
    print("AgentHub Result Ranker — Demo Mode")
    print("=" * 60)
    print()
    print("Session: 20260317-143022")
    print("Eval: pytest bench.py --json")
    print("Metric: p50_ms (lower is better)")
    print("Baseline: 180ms")
    print()

    header = f"{'RANK':<6} {'AGENT':<10} {'METRIC':<10} {'DELTA':<10} {'FILES':<7} {'SUMMARY'}"
    print(header)
    print("-" * 75)
    print(f"{'1':<6} {'agent-2':<10} {'142ms':<10} {'-38ms':<10} {'2':<7} Replaced O(n²) with hash map lookup")
    print(f"{'2':<6} {'agent-1':<10} {'165ms':<10} {'-15ms':<10} {'3':<7} Added caching layer")
    print(f"{'3':<6} {'agent-3':<10} {'190ms':<10} {'+10ms':<10} {'1':<7} Minor loop optimizations")
    print()
    print("Winner: agent-2 (142ms, -21% from baseline)")
    print()
    print("Next step: Run /hub:merge to merge agent-2's branch")
