# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from revenue_forecast_model_base import *  # noqa: F403,E402


def fmt_currency(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"
def fmt_pct(value):
    return f"{value * 100:.1f}%"
def print_header(title):
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)
def print_section(title):
    print(f"\n--- {title} ---")
