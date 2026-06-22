# ruff: noqa: F403, F405, E501
"""
Compliance Checker - Verify security compliance against SOC 2, PCI-DSS, HIPAA, GDPR.

Table of Contents:
    ComplianceChecker - Main class for compliance verification
        __init__         - Initialize with target path and framework
        check()          - Run compliance checks for selected framework
        check_soc2()     - Check SOC 2 Type II controls
        check_pci_dss()  - Check PCI-DSS v4.0 requirements
        check_hipaa()    - Check HIPAA security rule requirements
        check_gdpr()     - Check GDPR data protection requirements
        _check_encryption_at_rest() - Verify data encryption
        _check_access_controls() - Verify access control implementation
        _check_logging()  - Verify audit logging
        _check_secrets_management() - Verify secrets handling
        _calculate_compliance_score() - Calculate overall compliance score
    main() - CLI entry point

Usage:
    python compliance_checker.py /path/to/project
    python compliance_checker.py /path/to/project --framework soc2
    python compliance_checker.py /path/to/project --framework pci-dss --output report.json
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


# fmt: off
__all__ = ['Dict', 'List', 'Optional', 'Path', 'Tuple', 'argparse', 'asdict', 'dataclass', 'datetime', 'json', 'os', 're', 'sys']  # noqa: E501
# fmt: on
