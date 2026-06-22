# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_load_tester_base import *  # noqa: F403,E402
# fmt: off
from api_load_tester_p2 import LoadTester  # noqa: E402,E501
from api_load_tester_p3 import compare_results, print_results  # noqa: E402,E501
# fmt: on


class APILoadTester:
    """Main load tester class with CLI integration."""

    def __init__(self, urls: List[str], method: str = 'GET', body: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None, concurrency: int = 10,
                 duration: float = 10.0, timeout: float = 30.0, compare: bool = False,
                 verbose: bool = False, verify_ssl: bool = True):
        self.urls = urls
        self.method = method
        self.body = body
        self.headers = headers or {}
        self.concurrency = concurrency
        self.duration = duration
        self.timeout = timeout
        self.compare = compare
        self.verbose = verbose
        self.verify_ssl = verify_ssl

    def run(self) -> Dict:
        """Execute load test(s) and return results."""
        results = []

        for url in self.urls:
            tester = LoadTester(
                url=url,
                method=self.method,
                body=self.body,
                headers=self.headers,
                concurrency=self.concurrency,
                duration=self.duration,
                timeout=self.timeout,
                verify_ssl=self.verify_ssl,
            )

            result = tester.run()
            results.append(result)

            if not self.compare:
                print_results(result, self.verbose)

        if self.compare and len(results) >= 2:
            compare_results(results[0], results[1])

        return {
            'status': 'success',
            'results': [asdict(r) for r in results],
        }
def parse_headers(header_args: Optional[List[str]]) -> Dict[str, str]:
    """Parse header arguments into dictionary."""
    headers = {}
    if header_args:
        for h in header_args:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()
    return headers
