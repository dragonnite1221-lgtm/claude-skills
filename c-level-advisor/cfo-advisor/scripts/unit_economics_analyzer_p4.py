# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from unit_economics_analyzer_base import *  # noqa: F403,E402
# fmt: off
from unit_economics_analyzer_p1 import ChannelData, CohortData  # noqa: E402,E501
# fmt: on


def make_sample_cohorts() -> list[CohortData]:
    """
    Series A SaaS company, 8 quarters of cohort data.
    Shows a business improving on all dimensions over time.
    """
    return [
        CohortData(
            label="Q1 2023", acquisition_period="Jan-Mar 2023",
            customers_acquired=12, total_cac_spend=54_000,
            gross_margin_pct=0.68,
            monthly_revenue=[
                10_200, 9_600, 9_100, 8_700, 8_300, 8_000,  # M1-M6
                7_800, 7_600, 7_400, 7_200, 7_000, 6_800,   # M7-M12
                6_700, 6_600, 6_500, 6_400, 6_300, 6_200,   # M13-M18
                6_100, 6_000, 5_900, 5_800, 5_700, 5_600,   # M19-M24
            ],
        ),
        CohortData(
            label="Q2 2023", acquisition_period="Apr-Jun 2023",
            customers_acquired=15, total_cac_spend=60_000,
            gross_margin_pct=0.69,
            monthly_revenue=[
                13_500, 12_900, 12_500, 12_100, 11_800, 11_500,
                11_300, 11_100, 10_900, 10_700, 10_500, 10_300,
                10_200, 10_100, 10_000, 9_900, 9_800, 9_700,
            ],
        ),
        CohortData(
            label="Q3 2023", acquisition_period="Jul-Sep 2023",
            customers_acquired=18, total_cac_spend=63_000,
            gross_margin_pct=0.70,
            monthly_revenue=[
                16_200, 15_800, 15_400, 15_100, 14_800, 14_600,
                14_400, 14_200, 14_000, 13_900, 13_800, 13_700,
                13_600, 13_500, 13_400, 13_300,
            ],
        ),
        CohortData(
            label="Q4 2023", acquisition_period="Oct-Dec 2023",
            customers_acquired=22, total_cac_spend=70_400,
            gross_margin_pct=0.71,
            monthly_revenue=[
                20_900, 20_500, 20_200, 19_900, 19_700, 19_500,
                19_300, 19_100, 19_000, 18_900, 18_800, 18_700,
            ],
        ),
        CohortData(
            label="Q1 2024", acquisition_period="Jan-Mar 2024",
            customers_acquired=28, total_cac_spend=81_200,
            gross_margin_pct=0.72,
            monthly_revenue=[
                27_200, 26_900, 26_600, 26_400, 26_200, 26_000,
                25_800, 25_700, 25_600, 25_500,
            ],
        ),
        CohortData(
            label="Q2 2024", acquisition_period="Apr-Jun 2024",
            customers_acquired=34, total_cac_spend=91_800,
            gross_margin_pct=0.72,
            monthly_revenue=[
                33_300, 33_000, 32_800, 32_600, 32_400, 32_200,
            ],
        ),
        CohortData(
            label="Q3 2024", acquisition_period="Jul-Sep 2024",
            customers_acquired=40, total_cac_spend=100_000,
            gross_margin_pct=0.73,
            monthly_revenue=[
                39_600, 39_400, 39_200,
            ],
        ),
        CohortData(
            label="Q4 2024", acquisition_period="Oct-Dec 2024",
            customers_acquired=47, total_cac_spend=112_800,
            gross_margin_pct=0.73,
            monthly_revenue=[
                47_000,
            ],
        ),
    ]
def make_sample_channels() -> list[ChannelData]:
    """
    Q4 2024 channel breakdown. Blended looks fine; per-channel reveals problems.
    """
    return [
        ChannelData("Organic / SEO",     spend=9_500,  customers_acquired=14, avg_arpa=950,  gross_margin_pct=0.73, avg_monthly_churn=0.015),
        ChannelData("Paid Search (SEM)",  spend=48_000, customers_acquired=18, avg_arpa=980,  gross_margin_pct=0.73, avg_monthly_churn=0.020),
        ChannelData("Paid Social",        spend=32_000, customers_acquired=8,  avg_arpa=900,  gross_margin_pct=0.72, avg_monthly_churn=0.025),
        ChannelData("Content / Inbound",  spend=11_000, customers_acquired=6,  avg_arpa=1100, gross_margin_pct=0.74, avg_monthly_churn=0.012),
        ChannelData("Outbound SDR",       spend=22_000, customers_acquired=4,  avg_arpa=1200, gross_margin_pct=0.73, avg_monthly_churn=0.022),
        ChannelData("Events / Webinars",  spend=18_500, customers_acquired=3,  avg_arpa=1050, gross_margin_pct=0.72, avg_monthly_churn=0.028),
        ChannelData("Partner / Referral", spend=7_800,  customers_acquired=7,  avg_arpa=1000, gross_margin_pct=0.73, avg_monthly_churn=0.013),
    ]
