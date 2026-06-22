# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402


class ComplianceCheckerMixin10:
    def _print_summary(self, result: Dict):
        """Print compliance summary."""
        print("\n" + "=" * 60)
        print("COMPLIANCE CHECK SUMMARY")
        print("=" * 60)
        print(f"Target: {result['target']}")
        print(f"Framework: {result['framework'].upper()}")
        print(f"Scan duration: {result['scan_duration_seconds']}s")
        print(f"Compliance score: {result['compliance_score']}% ({result['compliance_level']})")
        print()

        summary = result['summary']
        print(f"Controls checked: {summary['total']}")
        print(f"  Passed:  {summary['passed']}")
        print(f"  Failed:  {summary['failed']}")
        print(f"  Warning: {summary['warnings']}")
        print(f"  N/A:     {summary['not_applicable']}")
        print("=" * 60)

        # Show failed controls
        failed = [c for c in result['controls'] if c['status'] == 'failed']
        if failed:
            print("\nFailed controls requiring remediation:")
            for control in failed[:5]:
                print(f"\n  [{control['severity'].upper()}] {control['control_id']}")
                print(f"  {control['title']}")
                print(f"  Recommendation: {control['recommendation']}")
