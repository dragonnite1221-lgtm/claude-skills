# ruff: noqa: F403, F405, E501
"""
Forecast Builder

Driver-based revenue forecasting with 13-week rolling cash flow projection,
scenario modeling (base/bull/bear), and trend analysis using simple linear
regression (standard library only).

Usage:
    python forecast_builder.py forecast_data.json
    python forecast_builder.py forecast_data.json --format json
    python forecast_builder.py forecast_data.json --scenarios base,bull,bear
"""
import argparse
import json
import math
import sys
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Tuple', 'argparse', 'json', 'math', 'mean', 'sys']  # noqa: E501
# fmt: on
