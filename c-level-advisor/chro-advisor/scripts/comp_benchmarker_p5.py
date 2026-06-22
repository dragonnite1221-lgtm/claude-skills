# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comp_benchmarker_base import *  # noqa: F403,E402
# fmt: off
from comp_benchmarker_p1 import BandDefinition, CompRoster, Employee  # noqa: E402,E501
# fmt: on


def build_sample_roster() -> CompRoster:
    roster = CompRoster(
        company="AcmeTech (Series A)",
        as_of_date=date.today().isoformat(),
        funding_stage="Series A",
        comp_philosophy_target="P50",
        preferred_stock_price=8.50,
    )

    # Bands (Engineering, P50 target, Tier1 = SF/NYC)
    roster.bands = [
        BandDefinition("L2", "Engineering", 115_000, 132_000, 155_000, 110_000, 132_000, 155_000, "Tier1"),
        BandDefinition("L3", "Engineering", 148_000, 170_000, 198_000, 145_000, 170_000, 198_000, "Tier1"),
        BandDefinition("L4", "Engineering", 185_000, 215_000, 248_000, 182_000, 215_000, 250_000, "Tier1"),
        BandDefinition("M1", "Engineering", 170_000, 195_000, 225_000, 168_000, 195_000, 225_000, "Tier1"),
        BandDefinition("L2", "Engineering", 95_000, 108_000, 125_000, 92_000, 108_000, 126_000, "Tier2"),
        BandDefinition("L3", "Engineering", 122_000, 140_000, 162_000, 120_000, 140_000, 162_000, "Tier2"),
        BandDefinition("L2", "Sales",       80_000,  92_000, 108_000,  78_000,  92_000, 108_000, "Tier1"),
        BandDefinition("L3", "Sales",       95_000, 110_000, 128_000,  93_000, 110_000, 128_000, "Tier1"),
        BandDefinition("M1", "Sales",      130_000, 150_000, 172_000, 128_000, 150_000, 172_000, "Tier1"),
        BandDefinition("L2", "Product",    125_000, 145_000, 168_000, 123_000, 145_000, 168_000, "Tier1"),
        BandDefinition("L3", "Product",    155_000, 178_000, 205_000, 153_000, 178_000, 205_000, "Tier1"),
        BandDefinition("L2", "G&A",         85_000,  98_000, 115_000,  83_000,  98_000, 115_000, "Tier1"),
        BandDefinition("L3", "G&A",        110_000, 128_000, 148_000, 108_000, 128_000, 148_000, "Tier1"),
    ]

    roster.employees = [
        # Engineering — mix of scenarios
        Employee("E001", "Aarav Shah", "Senior SWE (Backend)", "L3", "Engineering", "Tier1",
                 base_salary=168_000, bonus_target_pct=0.0, equity_shares=40_000,
                 equity_strike=1.50, equity_current_409a=6.80, equity_vest_years_remaining=2.5,
                 benefits_annual=18_000, gender="M", ethnicity="Asian",
                 tenure_years=2.5, performance_rating=4, last_raise_months_ago=14,
                 last_equity_refresh_months_ago=None),

        Employee("E002", "Yuki Tanaka", "Senior SWE (Frontend)", "L3", "Engineering", "Tier1",
                 base_salary=152_000, bonus_target_pct=0.0, equity_shares=30_000,
                 equity_strike=2.20, equity_current_409a=6.80, equity_vest_years_remaining=0.5,
                 benefits_annual=18_000, gender="F", ethnicity="Asian",
                 tenure_years=3.8, performance_rating=5, last_raise_months_ago=11,
                 last_equity_refresh_months_ago=30),
        # Note: Yuki is high performer, near-vested, no recent refresh — flag expected

        Employee("E003", "Marcus Johnson", "SWE II (Backend)", "L2", "Engineering", "Tier1",
                 base_salary=110_000, bonus_target_pct=0.0, equity_shares=15_000,
                 equity_strike=2.50, equity_current_409a=6.80, equity_vest_years_remaining=3.0,
                 benefits_annual=15_000, gender="M", ethnicity="Black",
                 tenure_years=1.2, performance_rating=3, last_raise_months_ago=12,
                 last_equity_refresh_months_ago=None),
        # Note: Below band midpoint, recently hired — developing flag

        Employee("E004", "Priya Nair", "Staff SWE", "L4", "Engineering", "Tier1",
                 base_salary=222_000, bonus_target_pct=0.0, equity_shares=60_000,
                 equity_strike=0.80, equity_current_409a=6.80, equity_vest_years_remaining=2.0,
                 benefits_annual=18_000, gender="F", ethnicity="Asian",
                 tenure_years=4.2, performance_rating=5, last_raise_months_ago=8,
                 last_equity_refresh_months_ago=8),

        Employee("E005", "Tom Rivera", "SWE II (Platform)", "L2", "Engineering", "Tier2",
                 base_salary=88_000, bonus_target_pct=0.0, equity_shares=12_000,
                 equity_strike=3.00, equity_current_409a=6.80, equity_vest_years_remaining=2.5,
                 benefits_annual=14_000, gender="M", ethnicity="Hispanic",
                 tenure_years=1.8, performance_rating=4, last_raise_months_ago=22,
                 last_equity_refresh_months_ago=None),
        # Note: No raise in 22 months, high performer — flag expected

        Employee("E006", "Sarah Kim", "Eng Manager", "M1", "Engineering", "Tier1",
                 base_salary=192_000, bonus_target_pct=0.10, equity_shares=35_000,
                 equity_strike=1.20, equity_current_409a=6.80, equity_vest_years_remaining=1.8,
                 benefits_annual=18_000, gender="F", ethnicity="Asian",
                 tenure_years=2.8, performance_rating=4, last_raise_months_ago=9,
                 last_equity_refresh_months_ago=9),

        # Sales
        Employee("S001", "David Chen", "Account Executive (MM)", "L3", "Sales", "Tier1",
                 base_salary=105_000, bonus_target_pct=0.50, equity_shares=8_000,
                 equity_strike=3.50, equity_current_409a=6.80, equity_vest_years_remaining=2.0,
                 benefits_annual=15_000, gender="M", ethnicity="Asian",
                 tenure_years=1.5, performance_rating=3, last_raise_months_ago=15,
                 last_equity_refresh_months_ago=None),

        Employee("S002", "Amara Osei", "AE (Mid-Market)", "L3", "Sales", "Tier1",
                 base_salary=98_000, bonus_target_pct=0.50, equity_shares=6_000,
                 equity_strike=3.50, equity_current_409a=6.80, equity_vest_years_remaining=2.5,
                 benefits_annual=15_000, gender="F", ethnicity="Black",
                 tenure_years=1.0, performance_rating=4, last_raise_months_ago=12,
                 last_equity_refresh_months_ago=None),
        # Note: High performer, significantly below midpoint — flag expected

        Employee("S003", "Jordan Blake", "Sales Manager", "M1", "Sales", "Tier1",
                 base_salary=155_000, bonus_target_pct=0.20, equity_shares=20_000,
                 equity_strike=2.00, equity_current_409a=6.80, equity_vest_years_remaining=1.5,
                 benefits_annual=16_000, gender="NB", ethnicity="White",
                 tenure_years=2.2, performance_rating=3, last_raise_months_ago=10,
                 last_equity_refresh_months_ago=10),

        # Product
        Employee("P001", "Nina Patel", "Senior PM", "L3", "Product", "Tier1",
                 base_salary=176_000, bonus_target_pct=0.10, equity_shares=22_000,
                 equity_strike=1.80, equity_current_409a=6.80, equity_vest_years_remaining=2.0,
                 benefits_annual=17_000, gender="F", ethnicity="Asian",
                 tenure_years=2.0, performance_rating=4, last_raise_months_ago=12,
                 last_equity_refresh_months_ago=12),

        # G&A
        Employee("G001", "Chris Mueller", "Finance Manager", "L3", "G&A", "Tier1",
                 base_salary=125_000, bonus_target_pct=0.10, equity_shares=10_000,
                 equity_strike=2.80, equity_current_409a=6.80, equity_vest_years_remaining=3.0,
                 benefits_annual=16_000, gender="M", ethnicity="White",
                 tenure_years=1.5, performance_rating=3, last_raise_months_ago=15,
                 last_equity_refresh_months_ago=None),

        Employee("G002", "Fatima Al-Hassan", "HR Operations", "L2", "G&A", "Tier1",
                 base_salary=82_000, bonus_target_pct=0.08, equity_shares=5_000,
                 equity_strike=4.00, equity_current_409a=6.80, equity_vest_years_remaining=3.5,
                 benefits_annual=14_000, gender="F", ethnicity="Middle Eastern",
                 tenure_years=0.8, performance_rating=3, last_raise_months_ago=8,
                 last_equity_refresh_months_ago=None),
        # Note: Below band minimum — critical flag expected
    ]

    return roster
