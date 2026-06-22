# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from script_tester_base import *  # noqa: F403,E402
from script_tester_p0 import TestSuite  # noqa: F401,E501


class TestReportFormatter:
    """Formats test reports for output"""
    
    @staticmethod
    def format_json(test_suite: TestSuite) -> str:
        """Format test suite as JSON"""
        return json.dumps({
            "skill_path": test_suite.skill_path,
            "timestamp": test_suite.timestamp,
            "summary": test_suite.summary,
            "global_errors": test_suite.global_errors,
            "script_results": {
                name: {
                    "script_path": result.script_path,
                    "timestamp": result.timestamp,
                    "overall_status": result.overall_status,
                    "execution_time": round(result.execution_time, 2),
                    "tests": result.tests,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
                for name, result in test_suite.script_results.items()
            }
        }, indent=2)
        
    @staticmethod
    def format_human_readable(test_suite: TestSuite) -> str:
        """Format test suite as human-readable text"""
        lines = []
        lines.append("=" * 60)
        lines.append("SCRIPT TESTING REPORT")
        lines.append("=" * 60)
        lines.append(f"Skill: {test_suite.skill_path}")
        lines.append(f"Timestamp: {test_suite.timestamp}")
        lines.append("")
        
        # Summary
        if test_suite.summary:
            lines.append("SUMMARY:")
            lines.append(f"  Total Scripts: {test_suite.summary['total_scripts']}")
            lines.append(f"  Passed: {test_suite.summary['passed']}")
            lines.append(f"  Partial: {test_suite.summary['partial']}")
            lines.append(f"  Failed: {test_suite.summary['failed']}")
            lines.append(f"  Overall Status: {test_suite.summary['overall_status']}")
            lines.append("")
            
        # Global errors
        if test_suite.global_errors:
            lines.append("GLOBAL ERRORS:")
            for error in test_suite.global_errors:
                lines.append(f"  • {error}")
            lines.append("")
            
        # Individual script results
        for script_name, result in test_suite.script_results.items():
            lines.append(f"SCRIPT: {script_name}")
            lines.append(f"  Status: {result.overall_status}")
            lines.append(f"  Execution Time: {result.execution_time:.2f}s")
            lines.append("")
            
            # Tests
            if result.tests:
                lines.append("  TESTS:")
                for test_name, test_result in result.tests.items():
                    status = "✓ PASS" if test_result["passed"] else "✗ FAIL"
                    lines.append(f"    {status}: {test_result['message']}")
                lines.append("")
                
            # Errors
            if result.errors:
                lines.append("  ERRORS:")
                for error in result.errors:
                    lines.append(f"    • {error}")
                lines.append("")
                
            # Warnings
            if result.warnings:
                lines.append("  WARNINGS:")
                for warning in result.warnings:
                    lines.append(f"    • {warning}")
                lines.append("")
                
            lines.append("-" * 40)
            lines.append("")
            
        return "\n".join(lines)
