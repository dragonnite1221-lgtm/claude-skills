# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ai_threat_scanner_base import *  # noqa: F403,E402


def _csd_2(args, auth_required, findings):
    if auth_required:
        findings.insert(0, {
            "prompt_excerpt": "[AUTHORIZATION CHECK]",
            "signature_name": "authorization_required",
            "atlas_id": "AML.T0051",
            "atlas_name": "LLM Prompt Injection",
            "severity": "critical",
            "description": (
                f"Access level '{args.access_level}' requires explicit authorization. "
                "Use --authorized only after legal sign-off."
            ),
            "matched_pattern": "authorization_check",
        })
