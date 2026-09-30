"""Execute the real review consumers with deterministic validator processes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[1]


def prepare(root):
    (root / 'scripts').mkdir()
    shutil.copy(ROOT / 'scripts/required-skill-checks.py', root / 'scripts')
    skill = root / 'example skill'
    (skill / 'scripts').mkdir(parents=True)
    (skill / 'SKILL.md').write_text('---\nname: example\n---\n')
    (skill / 'scripts/example.py').touch()
    fixtures = {
        'engineering/skill-tester/scripts/skill_validator.py': {'overall_score': 95, 'compliance_level': 'EXCELLENT', 'checks': {'optional': {'passed': False}}, 'errors': []},
        'engineering/skill-security-auditor/scripts/skill_security_auditor.py': {'verdict': 'PASS', 'summary': {'critical': 0, 'high': 0}},
    }
    for name, data in fixtures.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('print(' + repr(json.dumps(data)) + ')\n')
    tester = root / 'engineering/skill-tester/scripts/script_tester.py'
    tester.write_text("import os, sys\nprint(os.environ['TESTER_JSON'])\nsys.exit(int(os.environ['TESTER_EXIT']))\n")
    bindir = root / 'bin'
    bindir.mkdir()
    tessl = bindir / 'tessl'
    tessl.write_text('#!/usr/bin/env python3\nimport os,sys\nprint(os.environ["TESSL_JSON"])\nsys.exit(int(os.environ["FAKE_TESSL_EXIT"]))\n')
    tessl.chmod(0o755)
    summary = {'total_scripts': 1, 'passed': 1, 'partial': 0, 'failed': 0, 'no_tests': 0, 'overall_status': 'PASS'}
    env = {**os.environ, 'PATH': str(bindir) + os.pathsep + os.environ['PATH'],
           'TESTER_JSON': json.dumps({'summary': summary, 'global_errors': []}), 'TESTER_EXIT': '0',
           'TESSL_JSON': json.dumps({'review': {'reviewScore': 95}, 'validation': {'overallPassed': True}}), 'FAKE_TESSL_EXIT': '0'}
    return skill, env, summary


@pytest.mark.parametrize('code,status,expected', [(0, 'PASS', '0'), (1, 'PARTIAL', '0'), (2, 'FAIL', '1'), (0, 'MALFORMED', '1'), (130, 'PASS', '1')])
def test_workflow_internal_gate(tmp_path, code, status, expected):
    skill, env, summary = prepare(tmp_path)
    summary.update(overall_status=status, passed=int(status == 'PASS'), partial=int(status == 'PARTIAL'), failed=int(status == 'FAIL'))
    env.update(TESTER_EXIT=str(code), TESTER_JSON=json.dumps({'summary': summary, 'global_errors': []}),
               SKILLS_JSON=json.dumps([str(skill)]), GITHUB_OUTPUT=str(tmp_path / 'output'))
    workflow = (ROOT / '.github/workflows/skill-quality-review.yml').read_text()
    step = workflow.split('      - name: Run internal validators\n', 1)[1].split('      - name:', 1)[0]
    body = textwrap.dedent(step.split('        run: |\n', 1)[1])
    result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', body], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    output = (tmp_path / 'output').read_text()
    assert 'internal_exit=' + expected in output
    report = Path(next(line.split('=', 1)[1] for line in output.splitlines() if line.startswith('internal_report=')))
    try:
        assert ('scripts ERROR' if status == 'MALFORMED' else status) in report.read_text()
    finally:
        report.unlink()


@pytest.mark.parametrize('exit_code,valid,expected', [(0, True, 0), (1, True, 1), (0, False, 1)])
def test_local_review_tessl_contract(tmp_path, exit_code, valid, expected):
    skill, env, _ = prepare(tmp_path)
    env.update(FAKE_TESSL_EXIT=str(exit_code), TESSL_JSON=json.dumps({'review': {'reviewScore': 95}, 'validation': {'overallPassed': valid}}))
    result = subprocess.run(['bash', str(ROOT / 'scripts/review-new-skills.sh'), str(skill)], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert result.returncode == expected, result.stdout + result.stderr
