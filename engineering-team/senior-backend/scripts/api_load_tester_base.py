# ruff: noqa: E501
#!/usr/bin/env python3
"""
API Load Tester

Performs HTTP load testing with configurable concurrency, measuring latency
percentiles, throughput, and error rates.

Usage:
    python api_load_tester.py https://api.example.com/users --concurrency 50 --duration 30
    python api_load_tester.py https://api.example.com/orders --method POST --body '{"item": 1}'
    python api_load_tester.py https://api.example.com/v1/users https://api.example.com/v2/users --compare
"""

import os
import sys
import json
import argparse
import time
import statistics
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
import ssl

__all__ = ['Dict', 'HTTPError', 'List', 'Optional', 'Request', 'ThreadPoolExecutor', 'Tuple', 'URLError', 'argparse', 'as_completed', 'asdict', 'dataclass', 'datetime', 'field', 'json', 'os', 'queue', 'ssl', 'statistics', 'sys', 'threading', 'time', 'urlopen', 'urlparse']
