# ruff: noqa: E501
#!/usr/bin/env python3
"""
seo_health_scorer.py — Weighted 0-100 SEO health score across 7 categories.

Inspired by the scoring methodology used in top SEO audit tools. Replaces
binary pass/fail with a quantified health score that enables trend tracking,
stakeholder reporting, and prioritized action plans.

Categories and default weights:
  Technical SEO:   22%  (crawlability, indexation, redirects, sitemaps, robots.txt)
  Content Quality: 23%  (thin content, duplicate, keyword stuffing, readability)
  On-Page SEO:     20%  (titles, metas, headings, internal links, alt text)
  Schema Markup:   10%  (JSON-LD, breadcrumbs, FAQ, product, article schemas)
  Performance:     10%  (Core Web Vitals thresholds: LCP, CLS, INP)
  AI Readiness:    10%  (answer-first format, citability, entity clarity)
  Images:           5%  (alt text, compression, lazy loading, format)

Each check within a category returns pass/warn/fail. Severity multipliers:
  pass = 1.0, warn = 0.5, fail = 0.0

Industry profiles adjust weights:
  SaaS      → Technical +5%, Content +5%, Schema -5%, Images -5%
  Ecommerce → Schema +5%, Images +5%, AI Readiness -5%, Content -5%
  Local     → On-Page +5%, Schema +5%, Technical -5%, AI Readiness -5%
  Publisher → Content +5%, AI Readiness +5%, Technical -5%, Schema -5%

Usage:
    python seo_health_scorer.py --checks checks.json
    python seo_health_scorer.py --checks checks.json --industry saas
    python seo_health_scorer.py --checks checks.json --json
    python seo_health_scorer.py --demo

Input format (checks.json):
    [
      {"category": "technical", "check": "robots.txt exists", "result": "pass", "severity": "critical"},
      {"category": "content", "check": "thin content pages", "result": "fail", "severity": "high", "detail": "12 pages < 300 words"},
      ...
    ]

Severity levels for priority ordering:
    critical — blocks indexation or causes penalties (fix immediately)
    high     — significantly impacts rankings (fix within 1 week)
    medium   — optimization opportunity (fix within 1 month)
    low      — backlog polish item
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

__all__ = ['Path', 'annotations', 'argparse', 'defaultdict', 'json', 'sys']
