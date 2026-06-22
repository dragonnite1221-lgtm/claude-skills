# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_analyzer_base import *  # noqa: F403,E402
# fmt: off
from unit_economics_analyzer_p1 import ChannelData, CohortData, UnitEconomicsResult, calc_ltv, calc_payback  # noqa: E402,E501
# fmt: on


def analyze_cohort(cohort: CohortData) -> UnitEconomicsResult:
    """Compute full unit economics for a cohort."""
    n = cohort.customers_acquired
    if n == 0:
        raise ValueError(f"Cohort {cohort.label}: customers_acquired cannot be 0")

    cac = cohort.total_cac_spend / n

    # ARPA from month 1 revenue
    m1_rev = cohort.monthly_revenue[0] if cohort.monthly_revenue else 0
    arpa = m1_rev / n if n > 0 else 0

    # Observed monthly churn from cohort data
    # Use revenue decline from M1 to M12 to estimate churn
    months_available = len(cohort.monthly_revenue)
    if months_available >= 12:
        m12_rev = cohort.monthly_revenue[11]
        # Revenue retention over 12 months: (M12/M1)^(1/11) per month on average
        # Implied monthly retention rate
        if m1_rev > 0 and m12_rev > 0:
            monthly_retention = (m12_rev / m1_rev) ** (1 / 11)
            monthly_churn = 1 - monthly_retention
        else:
            monthly_churn = 0.02  # default
    elif months_available >= 6:
        m6_rev = cohort.monthly_revenue[5]
        if m1_rev > 0 and m6_rev > 0:
            monthly_retention = (m6_rev / m1_rev) ** (1 / 5)
            monthly_churn = 1 - monthly_retention
        else:
            monthly_churn = 0.02
    else:
        monthly_churn = 0.02  # default if < 6 months data

    # Clamp to reasonable range
    monthly_churn = max(0.001, min(monthly_churn, 0.30))

    ltv = calc_ltv(arpa, cohort.gross_margin_pct, monthly_churn)
    payback = calc_payback(cac, arpa, cohort.gross_margin_pct)
    ltv_cac = ltv / cac if cac > 0 else float("inf")

    # Snapshot revenues
    def rev_at(month_idx: int) -> Optional[float]:
        if months_available > month_idx:
            return cohort.monthly_revenue[month_idx]
        return None

    m6 = rev_at(5)
    m12 = rev_at(11)
    m24 = rev_at(23)

    # Realized LTV through observed months (actual gross profit)
    m12_ltv = sum(cohort.monthly_revenue[:12]) * cohort.gross_margin_pct if months_available >= 12 else None

    # Retention rates
    ret_m6 = (m6 / m1_rev) if (m6 is not None and m1_rev > 0) else None
    ret_m12 = (m12 / m1_rev) if (m12 is not None and m1_rev > 0) else None

    return UnitEconomicsResult(
        label=cohort.label,
        customers=n,
        cac=cac,
        arpa=arpa,
        gross_margin_pct=cohort.gross_margin_pct,
        monthly_churn=monthly_churn,
        ltv=ltv,
        ltv_cac_ratio=ltv_cac,
        payback_months=payback,
        m1_revenue=m1_rev,
        m6_revenue=m6,
        m12_revenue=m12,
        m24_revenue=m24,
        m12_ltv=m12_ltv,
        retention_m6=ret_m6,
        retention_m12=ret_m12,
    )
def analyze_channel(ch: ChannelData) -> UnitEconomicsResult:
    """Compute unit economics for an acquisition channel."""
    if ch.customers_acquired == 0:
        raise ValueError(f"Channel {ch.channel}: customers_acquired cannot be 0")

    cac = ch.spend / ch.customers_acquired
    ltv = calc_ltv(ch.avg_arpa, ch.gross_margin_pct, ch.avg_monthly_churn)
    payback = calc_payback(cac, ch.avg_arpa, ch.gross_margin_pct)
    ltv_cac = ltv / cac if cac > 0 else float("inf")

    return UnitEconomicsResult(
        label=ch.channel,
        customers=ch.customers_acquired,
        cac=cac,
        arpa=ch.avg_arpa,
        gross_margin_pct=ch.gross_margin_pct,
        monthly_churn=ch.avg_monthly_churn,
        ltv=ltv,
        ltv_cac_ratio=ltv_cac,
        payback_months=payback,
    )
def blended_cac(channels: list[ChannelData]) -> float:
    total_spend = sum(c.spend for c in channels)
    total_customers = sum(c.customers_acquired for c in channels)
    return total_spend / total_customers if total_customers > 0 else 0
def blended_ltv(channels: list[ChannelData]) -> float:
    """Weighted average LTV by customers acquired."""
    total_customers = sum(c.customers_acquired for c in channels)
    if total_customers == 0:
        return 0
    weighted = sum(
        calc_ltv(c.avg_arpa, c.gross_margin_pct, c.avg_monthly_churn) * c.customers_acquired
        for c in channels
    )
    return weighted / total_customers
def fmt(value: float, prefix: str = "$", decimals: int = 0) -> str:
    if value == float("inf"):
        return "∞"
    if abs(value) >= 1_000_000:
        return f"{prefix}{value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{prefix}{value/1_000:.1f}K"
    return f"{prefix}{value:.{decimals}f}"
def pct(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value*100:.1f}%"
