# ruff: noqa: E501
#!/usr/bin/env python3
"""RFP/RFI Response Analyzer - Score coverage, identify gaps, and recommend bid/no-bid.

Parses RFP/RFI requirements and scores coverage using Full/Partial/Planned/Gap
categories. Generates weighted coverage scores, gap analysis with mitigation
strategies, effort estimation, and bid/no-bid recommendations.

Usage:
    python rfp_response_analyzer.py rfp_data.json
    python rfp_response_analyzer.py rfp_data.json --format json
    python rfp_response_analyzer.py rfp_data.json --format text
"""

import argparse
import json
import sys
from typing import Any


# Coverage status to score mapping

__all__ = ['Any', 'argparse', 'json', 'sys']
