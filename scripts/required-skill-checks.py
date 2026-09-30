#!/usr/bin/env python3
"""Run mandatory internal checks and emit compact shell-safe status fields."""

import json
import subprocess
import sys
from pathlib import Path


def run_json(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        start = result.stdout.index("{")
        data = json.loads(result.stdout[start:])
        return result.returncode, data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return -1, {}


def evaluate(skill_dir):
    python = sys.executable
    code, data = run_json([python, "engineering/skill-tester/scripts/skill_validator.py", skill_dir, "--json"])
    score, level = data.get("overall_score"), data.get("compliance_level")
    # Follow the producer's acceptance contract; optional failed checks are advisory.
    structure_ok = code == 0 and type(score) in (int, float) and score >= 60 and data.get("errors") == []
    structure = f"{score}/{level}" if type(score) in (int, float) and isinstance(level, str) else "ERROR"

    scripts, scripts_ok = "N/A", True
    if any((Path(skill_dir) / "scripts").glob("*.py")):
        code, data = run_json([python, "engineering/skill-tester/scripts/script_tester.py", skill_dir, "--json"])
        summary = data.get("summary")
        summary = summary if isinstance(summary, dict) else {}
        total, passed = summary.get("total_scripts"), summary.get("passed")
        partial, failed, no_tests = (summary.get(key, 0) for key in ("partial", "failed", "no_tests"))
        status = summary.get("overall_status")
        counts_ok = (
            all(type(value) is int and value >= 0 for value in (total, passed, partial, failed, no_tests))
            and total > 0 and passed + partial + failed + no_tests == total
        )
        scripts_ok = (
            counts_ok and data.get("global_errors") == [] and failed == 0
            and ((code == 0 and status == "PASS" and passed == total)
                 or (code == 1 and status == "PARTIAL" and passed + partial > 0
                     and partial + no_tests > 0))
        )
        scripts = f"{passed}/{total} {status}" if counts_ok and status in ("PASS", "PARTIAL", "FAIL") else "ERROR"

    code, data = run_json([python, "engineering/skill-security-auditor/scripts/skill_security_auditor.py", skill_dir, "--strict", "--json"])
    summary = data.get("summary")
    summary = summary if isinstance(summary, dict) else {}
    critical, high, verdict = summary.get("critical"), summary.get("high"), data.get("verdict")
    security_ok = (
        code == 0 and verdict in ("PASS", "WARN")
        and type(critical) is int and critical == 0 and type(high) is int and high == 0
    )
    security = f"{verdict} (critical:{critical}, high:{high})" if verdict in ("PASS", "WARN", "FAIL") else "ERROR"
    return structure, scripts, security, "PASS" if structure_ok and scripts_ok and security_ok else "FAIL"


if __name__ == "__main__":
    print("|".join(evaluate(sys.argv[1])))
