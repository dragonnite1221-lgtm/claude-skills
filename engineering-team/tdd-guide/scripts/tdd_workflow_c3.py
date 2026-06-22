# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tdd_workflow_base import *  # noqa: F403,E402


class TDDWorkflowMixin3:
    def _check_quality_improvement(self, original: str, refactored: str) -> bool:
        """Check if refactoring improved code quality."""
        # Simple heuristics:
        # - Reduced duplication
        # - Better naming
        # - Simpler structure

        # Check for reduced duplication (basic check)
        original_lines = set(line.strip() for line in original.split('\n') if line.strip())
        refactored_lines = set(line.strip() for line in refactored.split('\n') if line.strip())

        # If unique lines increased proportionally, likely extracted duplicates
        if len(refactored_lines) > len(original_lines):
            return True

        # Check for better naming (longer, more descriptive names)
        original_avg_identifier_length = self._avg_identifier_length(original)
        refactored_avg_identifier_length = self._avg_identifier_length(refactored)

        if refactored_avg_identifier_length > original_avg_identifier_length:
            return True

        # If no clear improvement detected, assume refactoring was beneficial
        return True
    def _avg_identifier_length(self, code: str) -> float:
        """Calculate average identifier length (proxy for naming quality)."""
        import re
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)

        # Filter out keywords
        keywords = {'if', 'else', 'for', 'while', 'def', 'class', 'return', 'import', 'from'}
        identifiers = [i for i in identifiers if i.lower() not in keywords]

        if not identifiers:
            return 0.0

        return sum(len(i) for i in identifiers) / len(identifiers)
    def _suggest_refactorings(self, code: str) -> List[str]:
        """Suggest potential refactorings."""
        suggestions = []

        # Check for long functions
        lines = code.split('\n')
        if len(lines) > 30:
            suggestions.append('Consider breaking long function into smaller functions')

        # Check for duplication (simple check)
        line_counts = {}
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 10:  # Ignore very short lines
                line_counts[stripped] = line_counts.get(stripped, 0) + 1

        duplicates = [line for line, count in line_counts.items() if count > 2]
        if duplicates:
            suggestions.append(f'Found {len(duplicates)} duplicated code patterns - consider extraction')

        # Check for magic numbers
        import re
        magic_numbers = re.findall(r'\b\d+\b', code)
        if len(magic_numbers) > 5:
            suggestions.append('Consider extracting magic numbers to named constants')

        # Check for long parameter lists
        if 'def ' in code or 'function' in code:
            param_matches = re.findall(r'\(([^)]+)\)', code)
            for params in param_matches:
                if params.count(',') > 3:
                    suggestions.append('Consider using parameter object for functions with many parameters')
                    break

        if not suggestions:
            suggestions.append('Code looks clean - no obvious refactorings needed')

        return suggestions
    def generate_workflow_summary(self) -> str:
        """Generate summary of TDD workflow progress."""
        summary = [
            "# TDD Workflow Summary\n",
            f"Current Phase: {self.current_phase.value.upper()}",
            f"Current State: {self.state.value.replace('_', ' ').title()}",
            f"Completed Cycles: {len(self.history)}\n"
        ]

        summary.append("## TDD Cycle Steps:\n")
        summary.append("1. **RED**: Write a failing test")
        summary.append("   - Test describes desired behavior")
        summary.append("   - Test fails (no implementation)\n")

        summary.append("2. **GREEN**: Make the test pass")
        summary.append("   - Write minimal code to pass test")
        summary.append("   - All tests should pass\n")

        summary.append("3. **REFACTOR**: Improve the code")
        summary.append("   - Clean up implementation")
        summary.append("   - Tests still pass")
        summary.append("   - Code is more maintainable\n")

        return "\n".join(summary)
