# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_architect_base import *  # noqa: F403,E402
from project_architect_p0 import PatternDetector  # noqa: F401,E501
from project_architect_p1 import LayerViolationDetector  # noqa: F401,E501


class ProjectArchitect:
    """Main class that orchestrates architecture analysis."""

    def __init__(self, project_path: Path, verbose: bool = False):
        self.project_path = project_path
        self.verbose = verbose

    def analyze(self) -> Dict:
        """Run full architecture analysis."""
        if self.verbose:
            print(f"Analyzing project: {self.project_path}")

        # Pattern detection
        pattern_detector = PatternDetector(self.project_path)
        pattern_result = pattern_detector.scan()

        if self.verbose:
            print(f"Detected pattern: {pattern_result['detected_pattern']} "
                  f"(confidence: {pattern_result['confidence']}%)")

        # Code analysis
        code_analyzer = CodeAnalyzer(self.project_path, self.verbose)
        code_result = code_analyzer.analyze()

        if self.verbose:
            print(f"Found {len(code_result['issues'])} code issues")

        # Layer violation detection
        violation_detector = LayerViolationDetector(
            self.project_path,
            pattern_result['layer_assignments']
        )
        violations = violation_detector.detect()

        if self.verbose:
            print(f"Found {len(violations)} layer violations")

        # Generate recommendations
        recommendations = self._generate_recommendations(
            pattern_result, code_result, violations
        )

        return {
            'project_path': str(self.project_path),
            'architecture': {
                'detected_pattern': pattern_result['detected_pattern'],
                'confidence': pattern_result['confidence'],
                'layer_assignments': pattern_result['layer_assignments'],
                'pattern_scores': pattern_result['pattern_scores'],
            },
            'structure': {
                'directories': pattern_result['directories'],
            },
            'code_quality': {
                'metrics': code_result['metrics'],
                'issues': code_result['issues'],
            },
            'layer_violations': violations,
            'recommendations': recommendations,
            'summary': {
                'pattern': pattern_result['detected_pattern'],
                'confidence': pattern_result['confidence'],
                'total_issues': len(code_result['issues']) + len(violations),
                'code_issues': len(code_result['issues']),
                'layer_violations': len(violations),
            },
        }

    def _generate_recommendations(self, pattern_result: Dict, code_result: Dict,
                                   violations: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Pattern recommendations
        pattern = pattern_result['detected_pattern']
        confidence = pattern_result['confidence']

        if pattern == 'unstructured' or confidence < 30:
            recommendations.append(
                "Consider adopting a clear architectural pattern (Layered, Clean, or Hexagonal) "
                "to improve code organization and maintainability"
            )

        # Layer violation recommendations
        if violations:
            recommendations.append(
                f"Fix {len(violations)} layer violation(s) to maintain proper separation of concerns. "
                "Dependencies should flow from presentation → application → domain ← infrastructure"
            )

        # God class recommendations
        god_classes = code_result['metrics'].get('god_classes', [])
        if god_classes:
            recommendations.append(
                f"Split {len(god_classes)} large class(es) into smaller, focused classes "
                "following the Single Responsibility Principle"
            )

        # Large file recommendations
        large_files = code_result['metrics'].get('large_files', [])
        if large_files:
            recommendations.append(
                f"Consider refactoring {len(large_files)} large file(s) into smaller modules"
            )

        # Missing layer recommendations
        assigned_layers = set(pattern_result['layer_assignments'].values())
        if pattern in ['layered', 'clean', 'hexagonal']:
            expected_layers = {'presentation', 'application', 'domain', 'infrastructure'}
            missing = expected_layers - assigned_layers - {'unknown'}
            if missing:
                recommendations.append(
                    f"Consider adding missing architectural layer(s): {', '.join(missing)}"
                )

        return recommendations
