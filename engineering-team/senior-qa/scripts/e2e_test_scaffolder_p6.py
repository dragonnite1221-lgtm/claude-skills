# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from e2e_test_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from e2e_test_scaffolder_p2 import RouteScanner  # noqa: E402,E501
from e2e_test_scaffolder_p3 import TestGenerator  # noqa: E402,E501
from e2e_test_scaffolder_p4 import PageObjectGenerator  # noqa: E402,E501
from e2e_test_scaffolder_p5 import ConfigGenerator  # noqa: E402,E501
# fmt: on


class E2ETestScaffolder:
    """Main scaffolder class"""

    def __init__(
        self,
        source_path: str,
        output_path: Optional[str] = None,
        include_pom: bool = False,
        routes: Optional[str] = None,
        verbose: bool = False
    ):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path) if output_path else Path('e2e')
        self.include_pom = include_pom
        self.routes_filter = routes.split(',') if routes else None
        self.verbose = verbose
        self.results = {
            'status': 'success',
            'source': str(self.source_path),
            'routes': [],
            'generated_files': [],
            'summary': {}
        }

    def run(self) -> Dict:
        """Run the scaffolder"""
        print(f"Scanning: {self.source_path}")

        # Validate source path
        if not self.source_path.exists():
            raise ValueError(f"Source path does not exist: {self.source_path}")

        # Scan for routes
        scanner = RouteScanner(self.source_path, self.verbose)
        routes = scanner.scan(self.routes_filter)

        print(f"Found {len(routes)} routes")

        # Create output directories
        self.output_path.mkdir(parents=True, exist_ok=True)
        if self.include_pom:
            (self.output_path / 'pages').mkdir(exist_ok=True)

        # Generate test files
        test_generator = TestGenerator(self.include_pom, self.verbose)
        pom_generator = PageObjectGenerator(self.verbose) if self.include_pom else None
        config_generator = ConfigGenerator()

        # Generate tests for each route
        for route in routes:
            # Generate test file
            test_content = test_generator.generate(route)
            test_filename = self._get_test_filename(route.path)
            test_path = self.output_path / test_filename

            test_path.write_text(test_content, encoding='utf-8')

            self.results['generated_files'].append({
                'type': 'test',
                'route': route.path,
                'path': str(test_path)
            })

            print(f"  {test_filename}")

            # Generate Page Object if enabled
            if self.include_pom:
                pom_content = pom_generator.generate(route)
                pom_filename = self._get_pom_filename(route.path)
                pom_path = self.output_path / 'pages' / pom_filename

                pom_path.write_text(pom_content, encoding='utf-8')

                self.results['generated_files'].append({
                    'type': 'page_object',
                    'route': route.path,
                    'path': str(pom_path)
                })

                print(f"  pages/{pom_filename}")

        # Generate config files if not exists
        config_path = Path('playwright.config.ts')
        if not config_path.exists():
            config_content = config_generator.generate_config()
            config_path.write_text(config_content, encoding='utf-8')
            self.results['generated_files'].append({
                'type': 'config',
                'path': str(config_path)
            })
            print(f"  playwright.config.ts")

        # Generate auth fixture
        fixtures_dir = self.output_path / 'fixtures'
        fixtures_dir.mkdir(exist_ok=True)
        auth_fixture_path = fixtures_dir / 'auth.ts'
        if not auth_fixture_path.exists():
            auth_content = config_generator.generate_auth_fixture()
            auth_fixture_path.write_text(auth_content, encoding='utf-8')
            self.results['generated_files'].append({
                'type': 'fixture',
                'path': str(auth_fixture_path)
            })
            print(f"  fixtures/auth.ts")

        # Store route info
        self.results['routes'] = [asdict(r) for r in routes]

        # Summary
        self.results['summary'] = {
            'total_routes': len(routes),
            'total_files': len(self.results['generated_files']),
            'output_directory': str(self.output_path),
            'include_pom': self.include_pom
        }

        print('')
        print(f"Summary: {len(routes)} routes, {len(self.results['generated_files'])} files generated")

        return self.results

    def _get_test_filename(self, route_path: str) -> str:
        """Get test filename from route path"""
        if route_path == '/':
            return 'home.spec.ts'

        name = route_path.strip('/')
        name = re.sub(r'\[([^\]]+)\]', r'\1', name)  # [id] -> id
        name = name.replace('/', '-')
        return f"{name}.spec.ts"

    def _get_pom_filename(self, route_path: str) -> str:
        """Get Page Object filename from route path"""
        if route_path == '/':
            return 'HomePage.ts'

        name = route_path.strip('/')
        name = re.sub(r'\[.*?\]', '', name)
        parts = name.split('/')
        class_name = ''.join(p.title() for p in parts if p) + 'Page'
        return f"{class_name}.ts"
