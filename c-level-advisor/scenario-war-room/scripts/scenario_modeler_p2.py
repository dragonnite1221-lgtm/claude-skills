# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from scenario_modeler_base import *  # noqa: F403,E402
# fmt: off
from scenario_modeler_p1 import Domain, Variable  # noqa: E402,E501
# fmt: on


def _generate_signals(var: Variable) -> List[str]:
    """Generate plausible early warning signals based on variable type."""
    signals = []
    name_lower = var.name.lower()

    if any(k in name_lower for k in ["customer", "churn", "account"]):
        signals = [
            "Executive sponsor unreachable for >2 weeks",
            "Product usage drops >20% month-over-month",
            "No QBR scheduled within 90 days of contract renewal",
            "Support ticket volume spikes >50% without explanation",
        ]
    elif any(k in name_lower for k in ["fundraise", "raise", "capital", "investor"]):
        signals = [
            "Fewer than 3 term sheets after 60 days of active process",
            "Lead investor requests 30+ day extension on diligence",
            "Comparable company raises at lower valuation (market signal)",
            "Investor meeting conversion rate below 20%",
        ]
    elif any(k in name_lower for k in ["engineer", "people", "team", "resign", "quit"]):
        signals = [
            "2+ engineers receive above-market counter-offer in 90 days",
            "Glassdoor activity increases from engineering team",
            "Key person requests 1:1 to 'talk about career' unexpectedly",
            "Referral interview requests from engineers increase",
        ]
    elif any(k in name_lower for k in ["market", "competitor", "competition"]):
        signals = [
            "Competitor raises $10M+ funding round",
            "Win/loss rate shifts >10% in 60 days",
            "Multiple prospects cite competitor by name in objections",
            "Competitor poaches 2+ of your customers in a quarter",
        ]
    else:
        signals = [
            f"Leading indicator for '{var.name}' deteriorates 20%+ vs baseline",
            "Weekly metric review shows 3-week trend in wrong direction",
            "External validation from customers or partners confirms risk",
        ]

    return signals[:3]  # Top 3
def _domain_to_owner(domain: Domain) -> str:
    mapping = {
        Domain.FINANCIAL: "CFO",
        Domain.REVENUE: "CRO",
        Domain.PRODUCT: "CPO",
        Domain.ENGINEERING: "CTO",
        Domain.PEOPLE: "CHRO",
        Domain.OPERATIONS: "COO",
        Domain.SECURITY: "CISO",
        Domain.MARKET: "CMO",
    }
    return mapping.get(domain, "CEO")
def identify_triggers(variables: List[Variable]) -> List[Dict]:
    """Generate early warning triggers for each variable."""
    triggers = []
    for var in variables:
        trigger = {
            "variable": var.name,
            "timeline": f"Watch from day 1; expect signal ~{var.timeline_days // 2} days before impact",
            "signals": _generate_signals(var),
            "response_owner": _domain_to_owner(var.affected_domains[0] if var.affected_domains else Domain.FINANCIAL),
        }
        triggers.append(trigger)
    return triggers
def format_currency(amount: int) -> str:
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    return f"${amount}"
