# ruff: noqa: F403, F405, E501
"""
Spec Validator - Validates a feature specification for completeness and quality.

Checks that a spec document contains all required sections, uses RFC 2119 keywords
correctly, has acceptance criteria in Given/When/Then format, and scores overall
completeness from 0-100.

Sections checked:
- Context, Functional Requirements, Non-Functional Requirements
- Acceptance Criteria, Edge Cases, API Contracts, Data Models, Out of Scope

Exit codes: 0 = pass, 1 = warnings, 2 = critical (or --strict with score < 80)

No external dependencies - uses only Python standard library.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


SECTIONS = [
    ("context", "Context", [r"^##\s+Context"], 10),
    ("functional_requirements", "Functional Requirements", [r"^##\s+Functional\s+Requirements"], 15),
    ("non_functional_requirements", "Non-Functional Requirements", [r"^##\s+Non-Functional\s+Requirements"], 10),
    ("acceptance_criteria", "Acceptance Criteria", [r"^##\s+Acceptance\s+Criteria"], 20),
    ("edge_cases", "Edge Cases", [r"^##\s+Edge\s+Cases"], 10),
    ("api_contracts", "API Contracts", [r"^##\s+API\s+Contracts"], 10),
    ("data_models", "Data Models", [r"^##\s+Data\s+Models"], 10),
    ("out_of_scope", "Out of Scope", [r"^##\s+Out\s+of\s+Scope"], 10),
    ("metadata", "Metadata (Author/Date/Status)", [r"\*\*Author:\*\*", r"\*\*Date:\*\*", r"\*\*Status:\*\*"], 5),
]


RFC_KEYWORDS = ["MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY"]


PLACEHOLDER_PATTERNS = [
    r"\[your\s+name\]",
    r"\[list\s+reviewers\]",
    r"\[describe\s+",
    r"\[input/condition\]",
    r"\[precondition\]",
    r"\[action\]",
    r"\[expected\s+result\]",
    r"\[feature/capability\]",
    r"\[operation\]",
    r"\[threshold\]",
    r"\[UI\s+component\]",
    r"\[service\]",
    r"\[percentage\]",
    r"\[number\]",
    r"\[METHOD\]",
    r"\[endpoint\]",
    r"\[Name\]",
    r"\[Entity\s+Name\]",
    r"\[type\]",
    r"\[constraints\]",
    r"\[field\]",
    r"\[reason\]",
]


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'PLACEHOLDER_PATTERNS', 'Path', 'RFC_KEYWORDS', 'SECTIONS', 'Tuple', 'argparse', 'json', 're', 'sys']  # noqa: E501
# fmt: on
