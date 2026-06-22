# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fundraising_model_base import *  # noqa: F403,E402
# fmt: off
from fundraising_model_p1 import RoundConfig, RoundResult, Shareholder  # noqa: E402,E501
from fundraising_model_p2 import CapTable  # noqa: E402,E501
# fmt: on


def build_sample_model() -> tuple[CapTable, list[RoundResult]]:
    """
    Sample company:
      - 2 founders, started with 10M shares each
      - 1M shares for early advisor
      - Raises Pre-seed → Seed → Series A → Series B → Series C
    """
    cap = CapTable()
    SHARES_PER_FOUNDER = 4_000_000
    SHARES_ADVISOR = 200_000

    # Founding state
    cap.add_shareholder(Shareholder("Founder A (CEO)", "common", SHARES_PER_FOUNDER))
    cap.add_shareholder(Shareholder("Founder B (CTO)", "common", SHARES_PER_FOUNDER))
    cap.add_shareholder(Shareholder("Advisor",         "common", SHARES_ADVISOR))

    rounds: list[RoundResult] = []
    prev_cap = cap.snapshot()

    # Round 1: Pre-seed — $500K at $4.5M pre, 10% option pool created
    r1 = cap.execute_round(RoundConfig(
        name="Pre-seed",
        pre_money_valuation=4_500_000,
        investment_amount=500_000,
        new_option_pool_pct=0.10,
        option_pool_pre_round=True,
        lead_investor_name="Angel Syndicate",
    ))
    rounds.append(r1)
    prev_r1 = r1.cap_table[:]

    # Round 2: Seed — $2M at $9M pre, expand option pool to 12%
    r2 = cap.execute_round(RoundConfig(
        name="Seed",
        pre_money_valuation=9_000_000,
        investment_amount=2_000_000,
        new_option_pool_pct=0.12,
        option_pool_pre_round=True,
        lead_investor_name="Seed Fund",
    ))
    rounds.append(r2)

    # Round 3: Series A — $12M at $38M pre, refresh option pool to 15%
    r3 = cap.execute_round(RoundConfig(
        name="Series A",
        pre_money_valuation=38_000_000,
        investment_amount=12_000_000,
        new_option_pool_pct=0.15,
        option_pool_pre_round=True,
        lead_investor_name="Series A Fund",
    ))
    rounds.append(r3)

    # Round 4: Series B — $25M at $95M pre, refresh pool to 12%
    r4 = cap.execute_round(RoundConfig(
        name="Series B",
        pre_money_valuation=95_000_000,
        investment_amount=25_000_000,
        new_option_pool_pct=0.12,
        option_pool_pre_round=True,
        lead_investor_name="Series B Fund",
    ))
    rounds.append(r4)

    # Round 5: Series C — $40M at $185M pre, refresh pool to 10%
    r5 = cap.execute_round(RoundConfig(
        name="Series C",
        pre_money_valuation=185_000_000,
        investment_amount=40_000_000,
        new_option_pool_pct=0.10,
        option_pool_pre_round=True,
        lead_investor_name="Series C Fund",
    ))
    rounds.append(r5)

    return cap, rounds
