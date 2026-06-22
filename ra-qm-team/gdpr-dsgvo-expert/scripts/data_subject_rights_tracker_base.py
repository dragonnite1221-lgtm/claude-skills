# ruff: noqa: F403, F405, E501
"""
Data Subject Rights Tracker

Tracks and manages data subject rights requests under GDPR Articles 15-22.
Monitors deadlines, generates response templates, and produces compliance reports.

Usage:
    python data_subject_rights_tracker.py list
    python data_subject_rights_tracker.py add --type access --subject "John Doe"
    python data_subject_rights_tracker.py status --id REQ-001
    python data_subject_rights_tracker.py report --output compliance_report.json
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4


RIGHTS_TYPES = {
    "access": {
        "article": "Art. 15",
        "name": "Right of Access",
        "deadline_days": 30,
        "description": "Data subject has the right to obtain confirmation of processing and access to their data",
        "response_includes": [
            "Purposes of processing",
            "Categories of personal data",
            "Recipients or categories of recipients",
            "Retention period or criteria",
            "Right to lodge complaint",
            "Source of data (if not collected from subject)",
            "Existence of automated decision-making"
        ]
    },
    "rectification": {
        "article": "Art. 16",
        "name": "Right to Rectification",
        "deadline_days": 30,
        "description": "Data subject has the right to have inaccurate personal data corrected",
        "response_includes": [
            "Confirmation of correction",
            "Details of corrected data",
            "Notification to recipients"
        ]
    },
    "erasure": {
        "article": "Art. 17",
        "name": "Right to Erasure (Right to be Forgotten)",
        "deadline_days": 30,
        "description": "Data subject has the right to have their personal data erased",
        "grounds": [
            "Data no longer necessary for original purpose",
            "Consent withdrawn",
            "Objection to processing (no overriding grounds)",
            "Unlawful processing",
            "Legal obligation to erase",
            "Data collected from child"
        ],
        "exceptions": [
            "Freedom of expression",
            "Legal obligation to retain",
            "Public health reasons",
            "Archiving in public interest",
            "Legal claims"
        ]
    },
    "restriction": {
        "article": "Art. 18",
        "name": "Right to Restriction of Processing",
        "deadline_days": 30,
        "description": "Data subject has the right to restrict processing of their data",
        "grounds": [
            "Accuracy contested (during verification)",
            "Processing is unlawful (erasure opposed)",
            "Controller no longer needs data (subject needs for legal claims)",
            "Objection pending verification"
        ]
    },
    "portability": {
        "article": "Art. 20",
        "name": "Right to Data Portability",
        "deadline_days": 30,
        "description": "Data subject has the right to receive their data in a portable format",
        "conditions": [
            "Processing based on consent or contract",
            "Processing carried out by automated means"
        ],
        "format_requirements": [
            "Structured format",
            "Commonly used format",
            "Machine-readable format"
        ]
    },
    "objection": {
        "article": "Art. 21",
        "name": "Right to Object",
        "deadline_days": 30,
        "description": "Data subject has the right to object to processing",
        "applies_to": [
            "Processing based on legitimate interests",
            "Processing for direct marketing",
            "Processing for research/statistics"
        ]
    },
    "automated": {
        "article": "Art. 22",
        "name": "Rights Related to Automated Decision-Making",
        "deadline_days": 30,
        "description": "Data subject has the right not to be subject to solely automated decisions",
        "includes": [
            "Right to human intervention",
            "Right to express point of view",
            "Right to contest decision"
        ]
    }
}


STATUSES = {
    "received": "Request received, pending identity verification",
    "verified": "Identity verified, processing request",
    "in_progress": "Gathering data / processing request",
    "pending_info": "Awaiting additional information from subject",
    "extended": "Deadline extended (complex request)",
    "completed": "Request completed and response sent",
    "refused": "Request refused (with justification)",
    "escalated": "Escalated to DPO/legal"
}


# fmt: off
__all__ = ['Dict', 'List', 'Optional', 'Path', 'RIGHTS_TYPES', 'STATUSES', 'argparse', 'datetime', 'json', 'os', 'sys', 'timedelta', 'uuid4']  # noqa: E501
# fmt: on
