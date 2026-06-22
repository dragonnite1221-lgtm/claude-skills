# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from fundraising_model_base import *  # noqa: F403,E402
# fmt: off
from fundraising_model_p1 import CapTableEntry, ExitAnalysis, RoundConfig, RoundResult, Shareholder  # noqa: E402,E501
# fmt: on


class CapTable:
    """Manages a cap table through multiple rounds."""

    def __init__(self):
        self.shareholders: list[Shareholder] = []
        self._total_shares: float = 0.0

    def add_shareholder(self, sh: Shareholder) -> None:
        self.shareholders.append(sh)
        self._total_shares += sh.shares

    def total_shares(self) -> float:
        return sum(s.shares for s in self.shareholders)

    def snapshot(self, label: str = "") -> list[CapTableEntry]:
        total = self.total_shares()
        return [
            CapTableEntry(
                name=s.name,
                share_class=s.share_class,
                shares=s.shares,
                pct_ownership=s.shares / total if total > 0 else 0,
                invested=s.invested,
                is_option_pool=s.is_option_pool,
            )
            for s in self.shareholders
        ]

    def execute_round(self, config: RoundConfig) -> RoundResult:
        """
        Execute a financing round:
        1. (Optional) Create option pool pre-round (dilutes existing shareholders)
        2. Issue new shares to investor at round price
        Returns a RoundResult with full cap table snapshot.
        """
        current_total = self.total_shares()

        # Step 1: Option pool shuffle (if pre-round)
        option_pool_shares_created = 0.0
        if config.new_option_pool_pct > 0 and config.option_pool_pre_round:
            # Target: post-round option pool = new_option_pool_pct of total post-money shares
            # Solve: pool_shares / (current_total + pool_shares + new_investor_shares) = target_pct
            # This requires iteration because new_investor_shares also depends on pool_shares
            # Simplification: create pool based on post-round total (slightly approximated)
            target_post_round_pct = config.new_option_pool_pct
            post_money = config.pre_money_valuation + config.investment_amount

            # Estimate shares per dollar (price per share)
            price_per_share = config.pre_money_valuation / current_total
            new_investor_shares_estimate = config.investment_amount / price_per_share

            # Pool shares needed so that pool / total_post = target_pct
            total_post_estimate = current_total + new_investor_shares_estimate
            pool_shares_needed = (target_post_round_pct * total_post_estimate) / (1 - target_post_round_pct)

            # Check if existing pool is sufficient
            existing_pool = next(
                (s.shares for s in self.shareholders if s.is_option_pool), 0
            )
            additional_pool_needed = max(0, pool_shares_needed - existing_pool)

            if additional_pool_needed > 0:
                option_pool_shares_created = additional_pool_needed
                # Add to existing pool or create new
                pool_sh = next((s for s in self.shareholders if s.is_option_pool), None)
                if pool_sh:
                    pool_sh.shares += additional_pool_needed
                else:
                    self.shareholders.append(Shareholder(
                        name="Option Pool",
                        share_class="option",
                        shares=additional_pool_needed,
                        is_option_pool=True,
                    ))

        # Step 2: Price per share (after pool creation)
        current_total_post_pool = self.total_shares()
        if config.share_price_override:
            price_per_share = config.share_price_override
        else:
            price_per_share = config.pre_money_valuation / current_total_post_pool

        # Step 3: New shares for investor
        new_shares = config.investment_amount / price_per_share

        # Step 4: Add investor to cap table
        self.shareholders.append(Shareholder(
            name=config.lead_investor_name,
            share_class="preferred",
            shares=new_shares,
            invested=config.investment_amount,
        ))

        post_money = config.pre_money_valuation + config.investment_amount
        total_post = self.total_shares()

        return RoundResult(
            round_name=config.name,
            pre_money_valuation=config.pre_money_valuation,
            investment_amount=config.investment_amount,
            post_money_valuation=post_money,
            price_per_share=price_per_share,
            new_shares_issued=new_shares,
            option_pool_shares_created=option_pool_shares_created,
            total_shares=total_post,
            cap_table=self.snapshot(),
        )

    def analyze_exit(self, exit_valuation: float) -> list[ExitAnalysis]:
        """
        Simple exit analysis: all preferred converts to common, proceeds split pro-rata.
        (Does not model liquidation preferences — see fundraising_playbook.md for that.)
        """
        total = self.total_shares()
        price_per_share = exit_valuation / total
        results = []
        for s in self.shareholders:
            if s.is_option_pool:
                continue  # unissued options don't receive proceeds
            proceeds = s.shares * price_per_share
            moic = proceeds / s.invested if s.invested > 0 else 0.0
            results.append(ExitAnalysis(
                exit_valuation=exit_valuation,
                shareholder=s.name,
                shares=s.shares,
                ownership_pct=s.shares / total,
                proceeds_common=proceeds,
                invested=s.invested,
                moic=moic,
            ))
        return sorted(results, key=lambda x: x.proceeds_common, reverse=True)
