# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_load_tester_base import *  # noqa: F403,E402
# fmt: off
from api_load_tester_p1 import HTTPClient, LoadTestResults, RequestResult, calculate_percentile  # noqa: E402,E501
# fmt: on


class LoadTester:
    """HTTP load testing engine."""

    def __init__(self, url: str, method: str = 'GET', body: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None, concurrency: int = 10,
                 duration: float = 10.0, timeout: float = 30.0, verify_ssl: bool = True):
        self.url = url
        self.method = method.upper()
        self.body = body.encode() if body else None
        self.headers = headers or {}
        self.concurrency = concurrency
        self.duration = duration
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.results: List[RequestResult] = []
        self.stop_event = threading.Event()
        self.results_lock = threading.Lock()

    def run(self) -> LoadTestResults:
        """Execute load test and return results."""
        print(f"Load Testing: {self.url}")
        print(f"Method: {self.method}")
        print(f"Concurrency: {self.concurrency}")
        print(f"Duration: {self.duration}s")
        print("-" * 50)

        self.results = []
        self.stop_event.clear()

        start_time = time.time()

        # Start worker threads
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = []
            for _ in range(self.concurrency):
                future = executor.submit(self._worker)
                futures.append(future)

            # Wait for duration
            time.sleep(self.duration)
            self.stop_event.set()

            # Wait for workers to finish
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Worker error: {e}")

        elapsed_time = time.time() - start_time

        return self._aggregate_results(elapsed_time)

    def _worker(self):
        """Worker thread that continuously sends requests."""
        client = HTTPClient(
            timeout=self.timeout,
            headers=self.headers,
            verify_ssl=self.verify_ssl,
        )

        while not self.stop_event.is_set():
            result = client.request(self.url, self.method, self.body)

            with self.results_lock:
                self.results.append(result)

    def _aggregate_results(self, elapsed_time: float) -> LoadTestResults:
        """Aggregate individual results into summary."""
        if not self.results:
            return LoadTestResults(
                target_url=self.url,
                method=self.method,
                duration_seconds=elapsed_time,
                concurrency=self.concurrency,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                requests_per_second=0,
                latency_min=0,
                latency_max=0,
                latency_avg=0,
                latency_p50=0,
                latency_p90=0,
                latency_p95=0,
                latency_p99=0,
                latency_stddev=0,
            )

        # Separate successful and failed
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        # Latency calculations (from successful requests)
        latencies = sorted([r.latency_ms for r in successful]) if successful else [0]

        # Error breakdown
        errors_by_type: Dict[str, int] = {}
        for r in failed:
            error_type = r.error or 'Unknown'
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        # Calculate throughput
        total_bytes = sum(r.response_size for r in successful)
        throughput_mbps = (total_bytes * 8) / (elapsed_time * 1_000_000) if elapsed_time > 0 else 0

        return LoadTestResults(
            target_url=self.url,
            method=self.method,
            duration_seconds=elapsed_time,
            concurrency=self.concurrency,
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            requests_per_second=len(self.results) / elapsed_time if elapsed_time > 0 else 0,
            latency_min=min(latencies),
            latency_max=max(latencies),
            latency_avg=statistics.mean(latencies) if latencies else 0,
            latency_p50=calculate_percentile(latencies, 50),
            latency_p90=calculate_percentile(latencies, 90),
            latency_p95=calculate_percentile(latencies, 95),
            latency_p99=calculate_percentile(latencies, 99),
            latency_stddev=statistics.stdev(latencies) if len(latencies) > 1 else 0,
            errors_by_type=errors_by_type,
            total_bytes_received=total_bytes,
            throughput_mbps=throughput_mbps,
        )
