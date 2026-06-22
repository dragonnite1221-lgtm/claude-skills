# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_linter_base import *  # noqa: F403,E402


@dataclass
class LintIssue:
    """Represents a linting issue found in the API specification."""
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str
    path: str
    suggestion: str = ""
    line_number: Optional[int] = None


@dataclass
class LintReport:
    """Complete linting report with issues and statistics."""
    issues: List[LintIssue] = field(default_factory=list)
    total_endpoints: int = 0
    endpoints_with_issues: int = 0
    score: float = 0.0
    
    def add_issue(self, issue: LintIssue) -> None:
        """Add an issue to the report."""
        self.issues.append(issue)
    
    def get_issues_by_severity(self) -> Dict[str, List[LintIssue]]:
        """Group issues by severity level."""
        grouped = {'error': [], 'warning': [], 'info': []}
        for issue in self.issues:
            if issue.severity in grouped:
                grouped[issue.severity].append(issue)
        return grouped
    
    def calculate_score(self) -> float:
        """Calculate overall API quality score (0-100)."""
        if self.total_endpoints == 0:
            return 100.0
        
        error_penalty = len([i for i in self.issues if i.severity == 'error']) * 10
        warning_penalty = len([i for i in self.issues if i.severity == 'warning']) * 3
        info_penalty = len([i for i in self.issues if i.severity == 'info']) * 1
        
        total_penalty = error_penalty + warning_penalty + info_penalty
        base_score = 100.0
        
        # Penalty per endpoint to normalize across API sizes
        penalty_per_endpoint = total_penalty / self.total_endpoints if self.total_endpoints > 0 else total_penalty
        
        self.score = max(0.0, base_score - penalty_per_endpoint)
        return self.score
