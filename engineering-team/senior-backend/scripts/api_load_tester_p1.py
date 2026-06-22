# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_load_tester_base import *  # noqa: F403,E402


@dataclass
class RequestResult:
    """Result of a single HTTP request."""
    success: bool
    status_code: int
    latency_ms: float
    error: Optional[str] = None
    response_size: int = 0
@dataclass
class LoadTestResults:
    """Aggregated load test results."""
    target_url: str
    method: str
    duration_seconds: float
    concurrency: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float

    # Latency metrics (milliseconds)
    latency_min: float
    latency_max: float
    latency_avg: float
    latency_p50: float
    latency_p90: float
    latency_p95: float
    latency_p99: float
    latency_stddev: float

    # Error breakdown
    errors_by_type: Dict[str, int] = field(default_factory=dict)

    # Transfer metrics
    total_bytes_received: int = 0
    throughput_mbps: float = 0.0

    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
def calculate_percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile from sorted data."""
    if not data:
        return 0.0
    k = (len(data) - 1) * (percentile / 100)
    f = int(k)
    c = f + 1 if f + 1 < len(data) else f
    return data[f] + (data[c] - data[f]) * (k - f)
class HTTPClient:
    """HTTP client with configurable settings."""

    def __init__(self, timeout: float = 30.0, headers: Optional[Dict[str, str]] = None,
                 verify_ssl: bool = True):
        self.timeout = timeout
        self.headers = headers or {}
        self.verify_ssl = verify_ssl

        # Create SSL context
        if not verify_ssl:
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self.ssl_context = None

    def request(self, url: str, method: str = 'GET', body: Optional[bytes] = None) -> RequestResult:
        """Execute HTTP request and return result."""
        start_time = time.perf_counter()

        try:
            request = Request(url, data=body, method=method)

            # Add headers
            for key, value in self.headers.items():
                request.add_header(key, value)

            # Add content-type for POST/PUT
            if body and method in ['POST', 'PUT', 'PATCH']:
                if 'Content-Type' not in self.headers:
                    request.add_header('Content-Type', 'application/json')

            # Execute request
            with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
                response_data = response.read()
                elapsed = (time.perf_counter() - start_time) * 1000

                return RequestResult(
                    success=True,
                    status_code=response.status,
                    latency_ms=elapsed,
                    response_size=len(response_data),
                )

        except HTTPError as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                success=False,
                status_code=e.code,
                latency_ms=elapsed,
                error=f"HTTP {e.code}: {e.reason}",
            )

        except URLError as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                success=False,
                status_code=0,
                latency_ms=elapsed,
                error=f"Connection error: {str(e.reason)}",
            )

        except TimeoutError:
            elapsed = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                success=False,
                status_code=0,
                latency_ms=elapsed,
                error="Connection timeout",
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            return RequestResult(
                success=False,
                status_code=0,
                latency_ms=elapsed,
                error=str(e),
            )
