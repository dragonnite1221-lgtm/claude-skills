# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402
from api_scaffolder_p0 import load_spec  # noqa: F401,E501


class APIScaffolderMixin0:
    """Generate Express.js routes from OpenAPI specification."""
    SUPPORTED_FRAMEWORKS = ['express', 'fastify', 'koa']
    def __init__(self, spec_path: str, output_dir: str, framework: str = 'express',
                 types_only: bool = False, verbose: bool = False):
        self.spec_path = Path(spec_path)
        self.output_dir = Path(output_dir)
        self.framework = framework
        self.types_only = types_only
        self.verbose = verbose
        self.spec: Dict = {}
        self.generated_files: List[str] = []
    def run(self) -> Dict:
        """Execute scaffolding process."""
        print(f"API Scaffolder - {self.framework.capitalize()}")
        print(f"Spec: {self.spec_path}")
        print(f"Output: {self.output_dir}")
        print("-" * 50)

        self.validate()
        self.load_spec()
        self.ensure_output_dir()

        if self.types_only:
            self.generate_types()
        else:
            self.generate_types()
            self.generate_validators()
            self.generate_routes()
            self.generate_index()

        return {
            'status': 'success',
            'spec': str(self.spec_path),
            'output': str(self.output_dir),
            'framework': self.framework,
            'generated_files': self.generated_files,
            'routes_count': len(self.get_operations()),
            'types_count': len(self.get_schemas()),
        }
    def validate(self):
        """Validate inputs."""
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {self.spec_path}")

        if self.framework not in self.SUPPORTED_FRAMEWORKS:
            raise ValueError(f"Unsupported framework: {self.framework}")
    def load_spec(self):
        """Load and parse OpenAPI specification."""
        self.spec = load_spec(self.spec_path)

        if self.verbose:
            title = self.spec.get('info', {}).get('title', 'Unknown')
            version = self.spec.get('info', {}).get('version', '0.0.0')
            print(f"Loaded: {title} v{version}")
    def ensure_output_dir(self):
        """Create output directory if needed."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def get_schemas(self) -> Dict:
        """Get component schemas from spec."""
        return self.spec.get('components', {}).get('schemas', {})
    def get_operations(self) -> List[Dict]:
        """Extract all operations from spec."""
        operations = []
        paths = self.spec.get('paths', {})

        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue

            for method, details in methods.items():
                if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
                    continue

                if not isinstance(details, dict):
                    continue

                op_id = details.get('operationId', f'{method}_{path}'.replace('/', '_'))

                operations.append({
                    'path': path,
                    'method': method.lower(),
                    'operation_id': op_id,
                    'summary': details.get('summary', ''),
                    'parameters': details.get('parameters', []),
                    'request_body': details.get('requestBody', {}),
                    'responses': details.get('responses', {}),
                    'tags': details.get('tags', ['default']),
                })

        return operations
