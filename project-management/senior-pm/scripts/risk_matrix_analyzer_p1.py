# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_analyzer_base import *  # noqa: F403,E402


RISK_CATEGORIES = {
    "technical": {
        "weight": 1.2,
        "description": "Technology, architecture, integration risks",
        "mitigation_strategies": [
            "Proof of concept development",
            "Technical spike implementation",
            "Expert consultation",
            "Alternative technology evaluation",
            "Incremental development approach"
        ]
    },
    "resource": {
        "weight": 1.1,
        "description": "Team capacity, skills, availability risks",
        "mitigation_strategies": [
            "Resource planning and buffer allocation",
            "Skill development and training",
            "Cross-training and knowledge sharing",
            "Contractor or consultant engagement",
            "Timeline adjustment for capacity"
        ]
    },
    "schedule": {
        "weight": 1.0,
        "description": "Timeline, deadline, dependency risks",
        "mitigation_strategies": [
            "Critical path analysis and optimization",
            "Buffer time allocation",
            "Dependency management and coordination",
            "Scope prioritization and phasing",
            "Parallel work streams where possible"
        ]
    },
    "business": {
        "weight": 1.3,
        "description": "Market, customer, competitive risks",
        "mitigation_strategies": [
            "Market research and validation",
            "Customer feedback integration",
            "Competitive analysis monitoring",
            "Stakeholder engagement strategy",
            "Business case validation checkpoints"
        ]
    },
    "financial": {
        "weight": 1.4,
        "description": "Budget, ROI, cost overrun risks",
        "mitigation_strategies": [
            "Detailed cost estimation and tracking",
            "Budget reserve allocation",
            "Regular financial checkpoint reviews",
            "Cost-benefit analysis updates",
            "Alternative funding source identification"
        ]
    },
    "regulatory": {
        "weight": 1.5,
        "description": "Compliance, legal, governance risks",
        "mitigation_strategies": [
            "Legal review and approval processes",
            "Compliance audit preparation",
            "Regulatory body engagement",
            "Documentation and audit trail maintenance",
            "External legal counsel consultation"
        ]
    },
    "external": {
        "weight": 1.0,
        "description": "Vendor, partner, environmental risks",
        "mitigation_strategies": [
            "Vendor assessment and backup options",
            "Contract negotiation and SLA definition",
            "Environmental monitoring and adaptation",
            "Partner relationship management",
            "External dependency tracking"
        ]
    }
}
PROBABILITY_LEVELS = {
    1: {"label": "Very Low", "range": "0-10%", "description": "Highly unlikely to occur"},
    2: {"label": "Low", "range": "11-30%", "description": "Unlikely but possible"},
    3: {"label": "Medium", "range": "31-60%", "description": "Moderate likelihood"},
    4: {"label": "High", "range": "61-85%", "description": "Likely to occur"},
    5: {"label": "Very High", "range": "86-100%", "description": "Almost certain to occur"}
}
IMPACT_LEVELS = {
    1: {"label": "Very Low", "description": "Minimal impact on project success"},
    2: {"label": "Low", "description": "Minor delays or cost increases"},
    3: {"label": "Medium", "description": "Significant impact on timeline/budget"},
    4: {"label": "High", "description": "Major project disruption"},
    5: {"label": "Very High", "description": "Project failure or critical compromise"}
}
RISK_TOLERANCE_THRESHOLDS = {
    "low": 8,      # Risk score <= 8: Accept
    "medium": 15,  # Risk score 9-15: Monitor
    "high": 20,    # Risk score 16-20: Mitigate
    "critical": 25 # Risk score >20: Urgent action
}
MITIGATION_STRATEGIES = {
    "accept": "Monitor risk without active mitigation",
    "avoid": "Eliminate risk through scope or approach changes",
    "mitigate": "Reduce probability or impact through proactive measures",
    "transfer": "Share or transfer risk to third parties",
    "contingency": "Prepare response plan for risk occurrence"
}
