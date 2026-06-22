# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p0 import ComponentInfo  # noqa: F401,E501


class ComponentScanner:
    """Scans source files for React components"""

    # Patterns for detecting React components
    FUNCTIONAL_COMPONENT = re.compile(
        r'^(?:export\s+)?(?:const|function)\s+([A-Z][a-zA-Z0-9]*)\s*[=:]?\s*(?:\([^)]*\)\s*(?::\s*[^=]+)?\s*=>|function\s*\([^)]*\))',
        re.MULTILINE
    )

    ARROW_COMPONENT = re.compile(
        r'^(?:export\s+)?const\s+([A-Z][a-zA-Z0-9]*)\s*=\s*(?:React\.)?(?:memo|forwardRef)?\s*\(',
        re.MULTILINE
    )

    CLASS_COMPONENT = re.compile(
        r'^(?:export\s+)?class\s+([A-Z][a-zA-Z0-9]*)\s+extends\s+(?:React\.)?(?:Component|PureComponent)',
        re.MULTILINE
    )

    HOOK_PATTERN = re.compile(r'use([A-Z][a-zA-Z0-9]*)\s*\(')
    PROPS_PATTERN = re.compile(r'(?:props\.|{\s*([^}]+)\s*}\s*=\s*props|:\s*([A-Z][a-zA-Z0-9]*Props))')
    CONTEXT_PATTERN = re.compile(r'useContext\s*\(|\.Provider|\.Consumer')
    EFFECT_PATTERN = re.compile(r'useEffect\s*\(|useLayoutEffect\s*\(')
    STATE_PATTERN = re.compile(r'useState\s*\(|useReducer\s*\(|this\.state')
    CALLBACK_PATTERN = re.compile(r'on[A-Z][a-zA-Z]*\s*[=:]|handle[A-Z][a-zA-Z]*\s*[=:]')

    def __init__(self, source_path: Path, verbose: bool = False):
        self.source_path = source_path
        self.verbose = verbose
        self.components: List[ComponentInfo] = []

    def scan(self) -> List[ComponentInfo]:
        """Scan the source path for React components"""
        extensions = {'.tsx', '.jsx', '.ts', '.js'}

        for root, dirs, files in os.walk(self.source_path):
            # Skip node_modules and test directories
            dirs[:] = [d for d in dirs if d not in {'node_modules', '__tests__', 'test', 'tests', '.git'}]

            for file in files:
                if Path(file).suffix in extensions:
                    file_path = Path(root) / file
                    self._scan_file(file_path)

        return self.components

    def _scan_file(self, file_path: Path):
        """Scan a single file for components"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not read {file_path}: {e}")
            return

        # Skip test files
        if '.test.' in file_path.name or '.spec.' in file_path.name:
            return

        # Skip files without JSX indicators
        if 'return' not in content or ('<' not in content and 'jsx' not in content.lower()):
            # Could still be a hook
            if not self.HOOK_PATTERN.search(content):
                return

        # Find functional components
        for match in self.FUNCTIONAL_COMPONENT.finditer(content):
            name = match.group(1)
            self._add_component(name, file_path, content, 'functional')

        # Find arrow function components
        for match in self.ARROW_COMPONENT.finditer(content):
            name = match.group(1)
            component_type = 'functional'
            if 'memo(' in content:
                component_type = 'memo'
            elif 'forwardRef(' in content:
                component_type = 'forwardRef'
            self._add_component(name, file_path, content, component_type)

        # Find class components
        for match in self.CLASS_COMPONENT.finditer(content):
            name = match.group(1)
            self._add_component(name, file_path, content, 'class')

    def _add_component(self, name: str, file_path: Path, content: str, component_type: str):
        """Add a component to the list if not already present"""
        # Check if already added
        for comp in self.components:
            if comp.name == name and comp.file_path == str(file_path):
                return

        # Extract hooks used
        hooks = list(set(self.HOOK_PATTERN.findall(content)))

        # Extract prop names (simplified)
        props = []
        props_match = self.PROPS_PATTERN.search(content)
        if props_match:
            props_str = props_match.group(1) or ''
            props = [p.strip().split(':')[0].strip() for p in props_str.split(',') if p.strip()]

        # Extract imports
        imports = re.findall(r"import\s+(?:{[^}]+}|[^;]+)\s+from\s+['\"]([^'\"]+)['\"]", content)

        # Extract exports
        exports = re.findall(r"export\s+(?:default\s+)?(?:const|function|class)\s+(\w+)", content)

        component = ComponentInfo(
            name=name,
            file_path=str(file_path),
            component_type=component_type,
            has_props=bool(props) or 'props' in content.lower(),
            props=props[:10],  # Limit props
            has_hooks=hooks[:10],  # Limit hooks
            has_context=bool(self.CONTEXT_PATTERN.search(content)),
            has_effects=bool(self.EFFECT_PATTERN.search(content)),
            has_state=bool(self.STATE_PATTERN.search(content)),
            has_callbacks=bool(self.CALLBACK_PATTERN.search(content)),
            exports=exports[:5],
            imports=imports[:10]
        )

        self.components.append(component)

        if self.verbose:
            print(f"  Found: {name} ({component_type}) in {file_path.name}")
