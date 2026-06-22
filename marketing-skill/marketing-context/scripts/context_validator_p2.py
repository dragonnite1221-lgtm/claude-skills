# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from context_validator_base import *  # noqa: F403,E402
# fmt: off
from context_validator_p1 import print_report, validate_context  # noqa: E402,E501
# fmt: on


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validates marketing context completeness. "
                    "Scores 0-100 based on required and optional section coverage."
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Path to a marketing context markdown file. "
             "If omitted, runs demo with embedded sample data."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Also output results as JSON."
    )
    args = parser.parse_args()

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        content = filepath.read_text()
    else:
        # Demo with sample data
        content = """# Marketing Context
*Last updated: 2026-01-15*

## Product Overview
**One-liner:** AI-powered mobility analysis for elderly care
**What it does:** Smartphone-based fall risk assessment using computer vision
**Product category:** HealthTech / Digital Health
**Business model:** SaaS, per-facility licensing

## Target Audience
**Target companies:** Care facilities, nursing homes, 50+ beds
**Decision-makers:** Facility directors, quality managers
**Primary use case:** Automated fall risk assessment replacing manual observation
**Jobs to be done:**
- Reduce fall incidents by identifying high-risk residents
- Meet regulatory documentation requirements efficiently
- Give care staff actionable mobility insights

## Problems & Pain Points
**Core problem:** Manual fall risk assessment is subjective, time-consuming, and inconsistent
**Why alternatives fall short:**
- Manual observation takes 30+ minutes per resident
- Paper-based assessments are completed once per quarter at best
**What it costs them:** Falls cost €8,000-12,000 per incident, plus liability
**Emotional tension:** Staff fear missing warning signs, blame after incidents

## Competitive Landscape
**Direct:** Traditional gait labs — $50K+ hardware, need trained staff
**Secondary:** Wearable sensors — low compliance, residents remove them
**Indirect:** Manual observation — subjective, inconsistent

## Differentiation
**Key differentiators:**
- Uses standard smartphone (no special hardware)
- AI-powered analysis (objective, repeatable)
**Why customers choose us:** Fast, affordable, no hardware investment

## Customer Language
**How they describe the problem:**
- "We never know who's going to fall next"
- "The documentation takes forever"
**Words to use:** mobility analysis, fall prevention, care quality
**Words to avoid:** surveillance, monitoring, tracking

## Brand Voice
**Tone:** Professional, empathetic, evidence-based
**Personality:** Trustworthy, innovative, caring

## Proof Points
**Metrics:**
- 80+ care facilities served
- 30% reduction in fall incidents (pilot data)
**Customers:** Major care facility chains in Germany

## Goals
**Business goal:** Expand to 200+ facilities, enter Spain and Netherlands
**Conversion action:** Book a demo
"""
        print("[Using embedded sample data — pass a file path for real validation]")

    results = validate_context(content)
    print_report(results)

    if args.json:
        print(f"\n{json.dumps(results, indent=2)}")
