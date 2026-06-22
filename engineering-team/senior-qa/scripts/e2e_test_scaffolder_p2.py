# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from e2e_test_scaffolder_p1 import RouteInfo  # noqa: E402,E501
# fmt: on


class RouteScanner:
    """Scans Next.js directories for routes"""

    # Pattern to detect page files
    PAGE_PATTERNS = {
        'page.tsx', 'page.ts', 'page.jsx', 'page.js',  # App Router
        'index.tsx', 'index.ts', 'index.jsx', 'index.js'  # Pages Router
    }

    # Patterns indicating specific features
    FORM_PATTERNS = [
        r'<form', r'handleSubmit', r'onSubmit', r'useForm',
        r'<input', r'<textarea', r'<select'
    ]

    AUTH_PATTERNS = [
        r'auth', r'login', r'signin', r'signup', r'register',
        r'useAuth', r'useSession', r'getServerSession', r'withAuth'
    ]

    INTERACTION_PATTERNS = {
        'click': r'onClick|button|Button|<a\s|Link',
        'type': r'<input|<textarea|onChange',
        'select': r'<select|Dropdown|Select',
        'navigation': r'useRouter|router\.push|Link',
        'modal': r'Modal|Dialog|isOpen|onClose',
        'toggle': r'toggle|Switch|Checkbox',
        'upload': r'<input.*type=["\']file|upload|dropzone'
    }

    def __init__(self, source_path: Path, verbose: bool = False):
        self.source_path = source_path
        self.verbose = verbose
        self.routes: List[RouteInfo] = []
        self.is_app_router = self._detect_router_type()

    def _detect_router_type(self) -> bool:
        """Detect if using App Router or Pages Router"""
        # App Router: has 'app' directory with page.tsx files
        # Pages Router: has 'pages' directory with index.tsx files
        app_dir = self.source_path / 'app'
        if app_dir.exists() and list(app_dir.rglob('page.*')):
            return True

        return 'app' in str(self.source_path).lower()

    def scan(self, filter_routes: Optional[List[str]] = None) -> List[RouteInfo]:
        """Scan for all routes"""
        self._scan_directory(self.source_path)

        # Filter if specific routes requested
        if filter_routes:
            self.routes = [
                r for r in self.routes
                if any(fr in r.path for fr in filter_routes)
            ]

        return self.routes

    def _scan_directory(self, directory: Path, url_path: str = ''):
        """Recursively scan directory for routes"""
        if not directory.exists():
            return

        for item in directory.iterdir():
            if item.name.startswith('.') or item.name == 'node_modules':
                continue

            if item.is_dir():
                # Handle route groups (parentheses) and dynamic routes
                dir_name = item.name

                if dir_name.startswith('(') and dir_name.endswith(')'):
                    # Route group - doesn't add to URL path
                    self._scan_directory(item, url_path)
                elif dir_name.startswith('[') and dir_name.endswith(']'):
                    # Dynamic route
                    param_name = dir_name[1:-1]
                    if param_name.startswith('...'):
                        # Catch-all route
                        new_path = f"{url_path}/[...{param_name[3:]}]"
                    else:
                        new_path = f"{url_path}/[{param_name}]"
                    self._scan_directory(item, new_path)
                elif dir_name == 'api':
                    # API routes - scan but mark differently
                    self._scan_api_directory(item, '/api')
                else:
                    new_path = f"{url_path}/{dir_name}"
                    self._scan_directory(item, new_path)

            elif item.is_file():
                self._process_file(item, url_path)

    def _process_file(self, file_path: Path, url_path: str):
        """Process a potential page file"""
        if file_path.name not in self.PAGE_PATTERNS:
            return

        # Skip if it's a layout or other special file
        if any(x in file_path.name for x in ['layout', 'loading', 'error', 'template']):
            return

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return

        # Determine route path
        if url_path == '':
            route_path = '/'
        else:
            route_path = url_path

        # Detect dynamic parameters
        params = re.findall(r'\[([^\]]+)\]', route_path)
        has_params = len(params) > 0

        # Detect features
        has_form = any(re.search(p, content) for p in self.FORM_PATTERNS)
        has_auth = any(re.search(p, content, re.IGNORECASE) for p in self.AUTH_PATTERNS)

        # Detect interactions
        interactions = []
        for interaction, pattern in self.INTERACTION_PATTERNS.items():
            if re.search(pattern, content):
                interactions.append(interaction)

        route = RouteInfo(
            path=route_path,
            file_path=str(file_path),
            route_type='dynamic' if has_params else 'page',
            has_params=has_params,
            params=params,
            has_form=has_form,
            has_auth=has_auth,
            interactions=interactions
        )

        self.routes.append(route)

        if self.verbose:
            print(f"  Found route: {route_path}")

    def _scan_api_directory(self, directory: Path, url_path: str):
        """Scan API routes (mark them differently)"""
        for item in directory.iterdir():
            if item.is_dir():
                new_path = f"{url_path}/{item.name}"
                self._scan_api_directory(item, new_path)
            elif item.is_file() and item.suffix in {'.ts', '.tsx', '.js', '.jsx'}:
                # API routes don't get E2E tests typically
                pass
