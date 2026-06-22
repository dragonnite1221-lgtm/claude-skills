# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from _test_suite_generator_base import *  # noqa: F403,E402
from _test_suite_generator_p0 import ComponentInfo  # noqa: F401,E501
from _test_suite_generator_p1 import ComponentScanner  # noqa: F401,E501


class TestSuiteGenerator:
    """Main class for generating test suites"""

    def __init__(
        self,
        source_path: str,
        output_path: Optional[str] = None,
        include_a11y: bool = False,
        scan_only: bool = False,
        verbose: bool = False,
        template: Optional[str] = None
    ):
        self.source_path = Path(source_path)
        self.output_path = Path(output_path) if output_path else None
        self.include_a11y = include_a11y
        self.scan_only = scan_only
        self.verbose = verbose
        self.template = template
        self.results = {
            'status': 'success',
            'source': str(self.source_path),
            'components': [],
            'generated_files': [],
            'summary': {}
        }

    def run(self) -> Dict:
        """Execute the test suite generation"""
        print(f"Scanning: {self.source_path}")

        # Validate source path
        if not self.source_path.exists():
            raise ValueError(f"Source path does not exist: {self.source_path}")

        # Scan for components
        scanner = ComponentScanner(self.source_path, self.verbose)
        components = scanner.scan()

        print(f"Found {len(components)} React components")

        if self.scan_only:
            self._report_scan_results(components)
            return self.results

        # Generate tests
        if not self.output_path:
            # Default to __tests__ in source directory
            self.output_path = self.source_path / '__tests__'

        self.output_path.mkdir(parents=True, exist_ok=True)

        generator = TestGenerator(self.include_a11y, self.template)

        total_tests = 0
        for component in components:
            test_file = generator.generate(component)
            content = generator.format_test_file(test_file)

            # Write test file
            test_filename = f"{component.name}.test.tsx"
            test_path = self.output_path / test_filename

            test_path.write_text(content, encoding='utf-8')

            test_count = len(test_file.test_cases)
            total_tests += test_count

            self.results['generated_files'].append({
                'component': component.name,
                'path': str(test_path),
                'test_cases': test_count
            })

            print(f"  {test_filename} ({test_count} test cases)")

        # Store component info
        self.results['components'] = [asdict(c) for c in components]

        # Summary
        self.results['summary'] = {
            'total_components': len(components),
            'total_files': len(self.results['generated_files']),
            'total_test_cases': total_tests,
            'output_directory': str(self.output_path)
        }

        print('')
        print(f"Summary: {len(components)} test files, {total_tests} test cases")

        return self.results

    def _report_scan_results(self, components: List[ComponentInfo]):
        """Report scan results without generating tests"""
        print('')
        print("=" * 60)
        print("COMPONENT SCAN RESULTS")
        print("=" * 60)

        # Group by type
        by_type = {}
        for comp in components:
            comp_type = comp.component_type
            if comp_type not in by_type:
                by_type[comp_type] = []
            by_type[comp_type].append(comp)

        for comp_type, comps in sorted(by_type.items()):
            print(f"\n{comp_type.upper()} COMPONENTS ({len(comps)}):")
            for comp in comps:
                hooks_str = f" [hooks: {', '.join(comp.has_hooks[:3])}]" if comp.has_hooks else ""
                state_str = " [stateful]" if comp.has_state else ""
                print(f"  - {comp.name}{hooks_str}{state_str}")
                print(f"    {comp.file_path}")

        print('')
        print("=" * 60)
        print(f"Total: {len(components)} components")
        print("=" * 60)

        self.results['components'] = [asdict(c) for c in components]
        self.results['summary'] = {
            'total_components': len(components),
            'by_type': {k: len(v) for k, v in by_type.items()}
        }
