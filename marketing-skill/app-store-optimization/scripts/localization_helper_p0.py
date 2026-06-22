# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from localization_helper_base import *  # noqa: F403,E402


def plan_localization_strategy(
    current_market: str,
    budget_level: str,
    monthly_downloads: int
) -> Dict[str, Any]:
    """
    Convenience function to plan localization strategy.

    Args:
        current_market: Current market code
        budget_level: Budget level
        monthly_downloads: Current monthly downloads

    Returns:
        Complete localization plan
    """
    helper = LocalizationHelper()

    target_markets = helper.identify_target_markets(
        current_market=current_market,
        budget_level=budget_level
    )

    # Extract market codes
    market_codes = [m['language'] for m in target_markets['recommended_markets']]

    # Calculate ROI
    estimated_cost = float(target_markets['estimated_cost'].replace('$', '').replace(',', ''))

    roi_analysis = helper.calculate_localization_roi(
        market_codes,
        monthly_downloads,
        estimated_cost
    )

    return {
        'target_markets': target_markets,
        'roi_analysis': roi_analysis
    }
