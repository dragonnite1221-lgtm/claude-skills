# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402


class DependencyAnalyzerMixin3:
    def _detect_circular_dependencies(self):
        """Detect circular dependencies between internal modules."""
        # Build dependency graph
        graph = defaultdict(set)
        modules = set(self.internal_modules.keys())

        for module, imports in self.internal_modules.items():
            for imp in imports:
                # Check if import is an internal module
                for internal_module in modules:
                    if internal_module.lower() in imp.lower() and internal_module != module:
                        graph[module].add(internal_module)

        # Find cycles using DFS
        visited = set()
        rec_stack = set()
        cycles = []

        def find_cycles(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    find_cycles(neighbor, path)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in cycles:
                        cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for module in modules:
            if module not in visited:
                find_cycles(module, [])

        self.circular_deps = cycles

        if cycles:
            for cycle in cycles:
                self.issues.append({
                    'type': 'circular_dependency',
                    'severity': 'warning',
                    'message': f"Circular dependency: {' -> '.join(cycle)}"
                })

        if self.verbose:
            print(f"Found {len(self.circular_deps)} circular dependencies")
    def _calculate_coupling_score(self):
        """Calculate coupling score (0-100, lower is better)."""
        if not self.internal_modules:
            self.coupling_score = 0
            return

        # Count connections between modules
        total_modules = len(self.internal_modules)
        total_connections = 0
        modules = set(self.internal_modules.keys())

        for module, imports in self.internal_modules.items():
            for imp in imports:
                for internal_module in modules:
                    if internal_module.lower() in imp.lower() and internal_module != module:
                        total_connections += 1

        # Max possible connections (complete graph)
        max_connections = total_modules * (total_modules - 1) if total_modules > 1 else 1

        # Coupling score as percentage of max connections
        self.coupling_score = min(100, int((total_connections / max_connections) * 100))

        # Add penalty for circular dependencies
        self.coupling_score = min(100, self.coupling_score + len(self.circular_deps) * 10)

        if self.verbose:
            print(f"Coupling score: {self.coupling_score}/100")
