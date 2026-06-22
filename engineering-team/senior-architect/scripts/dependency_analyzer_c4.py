# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dependency_analyzer_base import *  # noqa: F403,E402


class DependencyAnalyzerMixin4:
    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        # Circular dependency recommendations
        if self.circular_deps:
            self.recommendations.append(
                "Extract shared interfaces or create a common module to break circular dependencies"
            )

        # High coupling recommendations
        if self.coupling_score > 70:
            self.recommendations.append(
                "High coupling detected. Consider applying SOLID principles and "
                "introducing abstraction layers"
            )

        # Too many dependencies
        if len(self.direct_deps) > 50:
            self.recommendations.append(
                f"Large dependency count ({len(self.direct_deps)}). "
                "Review for unused dependencies and consider bundle size impact"
            )

        # Check for known problematic packages (simplified check)
        problematic = {
            'lodash': 'Consider lodash-es or native methods for smaller bundle',
            'moment': 'Consider day.js or date-fns for smaller bundle',
            'request': 'Deprecated. Use axios, node-fetch, or native fetch',
        }

        for pkg, suggestion in problematic.items():
            if pkg in self.direct_deps:
                self.recommendations.append(f"{pkg}: {suggestion}")
    def _build_report(self) -> Dict:
        """Build the analysis report."""
        return {
            'project_path': str(self.project_path),
            'package_manager': self.package_manager,
            'summary': {
                'direct_dependencies': len(self.direct_deps),
                'dev_dependencies': len(self.dev_deps),
                'internal_modules': len(self.internal_modules),
                'coupling_score': self.coupling_score,
                'circular_dependencies': len(self.circular_deps),
                'issues': len(self.issues),
            },
            'dependencies': {
                'direct': self.direct_deps,
                'dev': self.dev_deps,
            },
            'internal_modules': {k: list(v) for k, v in self.internal_modules.items()},
            'circular_dependencies': self.circular_deps,
            'issues': self.issues,
            'recommendations': self.recommendations,
        }
