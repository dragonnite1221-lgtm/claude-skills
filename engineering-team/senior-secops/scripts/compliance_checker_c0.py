# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compliance_checker_base import *  # noqa: F403,E402
from compliance_checker_p0 import ComplianceControl  # noqa: F401,E501


class ComplianceCheckerMixin0:
    """Verify security compliance against industry frameworks."""
    FRAMEWORKS = ['soc2', 'pci-dss', 'hipaa', 'gdpr', 'all']
    def __init__(
        self,
        target_path: str,
        framework: str = "all",
        verbose: bool = False
    ):
        """
        Initialize the compliance checker.

        Args:
            target_path: Directory to scan
            framework: Compliance framework to check (soc2, pci-dss, hipaa, gdpr, all)
            verbose: Enable verbose output
        """
        self.target_path = Path(target_path)
        self.framework = framework.lower()
        self.verbose = verbose
        self.controls: List[ComplianceControl] = []
        self.files_scanned = 0
    def check(self) -> Dict:
        """
        Run compliance checks for selected framework.

        Returns:
            Dict with compliance results
        """
        print(f"Compliance Checker - Scanning: {self.target_path}")
        print(f"Framework: {self.framework.upper()}")
        print()

        if not self.target_path.exists():
            return {"status": "error", "message": f"Path not found: {self.target_path}"}

        start_time = datetime.now()

        # Run framework-specific checks
        if self.framework in ('soc2', 'all'):
            self.check_soc2()
        if self.framework in ('pci-dss', 'all'):
            self.check_pci_dss()
        if self.framework in ('hipaa', 'all'):
            self.check_hipaa()
        if self.framework in ('gdpr', 'all'):
            self.check_gdpr()

        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()

        # Calculate statistics
        passed = len([c for c in self.controls if c.status == 'passed'])
        failed = len([c for c in self.controls if c.status == 'failed'])
        warnings = len([c for c in self.controls if c.status == 'warning'])
        na = len([c for c in self.controls if c.status == 'not_applicable'])

        compliance_score = self._calculate_compliance_score()

        result = {
            "status": "completed",
            "target": str(self.target_path),
            "framework": self.framework,
            "scan_duration_seconds": round(scan_duration, 2),
            "compliance_score": compliance_score,
            "compliance_level": self._get_compliance_level(compliance_score),
            "summary": {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "not_applicable": na,
                "total": len(self.controls)
            },
            "controls": [asdict(c) for c in self.controls]
        }

        self._print_summary(result)

        return result
    def check_soc2(self):
        """Check SOC 2 Type II controls."""
        if self.verbose:
            print("  Checking SOC 2 Type II controls...")

        # CC1: Control Environment - Access Controls
        self._check_access_controls_soc2()

        # CC2: Communication and Information
        self._check_documentation()

        # CC3: Risk Assessment
        self._check_risk_assessment()

        # CC6: Logical and Physical Access Controls
        self._check_authentication()

        # CC7: System Operations
        self._check_logging()

        # CC8: Change Management
        self._check_change_management()
