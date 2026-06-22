# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from poc_planner_base import *  # noqa: F403,E402


DEFAULT_PHASES = [
    {
        "name": "Setup",
        "duration_weeks": 1,
        "description": "Environment provisioning, data migration, initial configuration",
        "activities": [
            "Provision POC environment",
            "Configure authentication and access",
            "Migrate sample data sets",
            "Set up monitoring and logging",
            "Conduct kickoff meeting with stakeholders",
        ],
    },
    {
        "name": "Core Testing",
        "duration_weeks": 2,
        "description": "Primary use case validation and integration testing",
        "activities": [
            "Execute primary use case scenarios",
            "Test core integrations",
            "Validate data flow and transformations",
            "Conduct mid-point review with stakeholders",
            "Document findings and adjust test plan",
        ],
    },
    {
        "name": "Advanced Testing",
        "duration_weeks": 1,
        "description": "Edge cases, performance testing, and security validation",
        "activities": [
            "Execute edge case scenarios",
            "Run performance and load tests",
            "Validate security controls and compliance",
            "Test disaster recovery and failover",
            "Test administrative workflows",
        ],
    },
    {
        "name": "Evaluation",
        "duration_weeks": 1,
        "description": "Scorecard completion, stakeholder review, and go/no-go decision",
        "activities": [
            "Complete evaluation scorecard",
            "Compile POC results documentation",
            "Conduct final stakeholder review",
            "Present go/no-go recommendation",
            "Gather lessons learned",
        ],
    },
]
DEFAULT_EVAL_CATEGORIES = {
    "Functionality": {
        "weight": 0.30,
        "criteria": [
            "Core feature completeness",
            "Use case coverage",
            "Customization flexibility",
            "Workflow automation",
        ],
    },
    "Performance": {
        "weight": 0.20,
        "criteria": [
            "Response time under load",
            "Throughput capacity",
            "Scalability characteristics",
            "Resource utilization",
        ],
    },
    "Integration": {
        "weight": 0.20,
        "criteria": [
            "API completeness and documentation",
            "Data migration ease",
            "Third-party connector availability",
            "Authentication/SSO integration",
        ],
    },
    "Usability": {
        "weight": 0.15,
        "criteria": [
            "User interface intuitiveness",
            "Learning curve assessment",
            "Documentation quality",
            "Admin console functionality",
        ],
    },
    "Support": {
        "weight": 0.15,
        "criteria": [
            "Technical support responsiveness",
            "Knowledge base quality",
            "Training resources availability",
            "Community and ecosystem",
        ],
    },
}
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def load_poc_data(filepath: str) -> dict[str, Any]:
    """Load and validate POC data from a JSON file.

    Args:
        filepath: Path to the JSON file containing POC data.

    Returns:
        Parsed POC data dictionary.

    Raises:
        SystemExit: If the file cannot be read or parsed.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    if "poc_name" not in data:
        print("Error: JSON must contain 'poc_name' field.", file=sys.stderr)
        sys.exit(1)

    return data
