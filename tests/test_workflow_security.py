"""Regression tests for trust boundaries in AI-powered workflows."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_WORKFLOW = ROOT / ".github" / "workflows" / "claude-code-review.yml"
CLAUDE_WORKFLOW = ROOT / ".github" / "workflows" / "claude.yml"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "ci-quality-gate.yml"
CODEX_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "sync-codex-skills.yml"
SMART_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "smart-sync.yml"
VIRUSTOTAL_WORKFLOW = ROOT / ".github" / "workflows" / "virustotal-scan.yml"
AUTOMATION_SETUP = ROOT / ".github" / "AUTOMATION_SETUP.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_pr_metadata_is_not_interpolated_into_shell_source() -> None:
    workflow = _text(REVIEW_WORKFLOW)

    assert 'PR_TITLE="${{ github.event.pull_request.title }}"' not in workflow
    assert (
        "PR_LABELS: ${{ toJSON(github.event.pull_request.labels.*.name) }}" in workflow
    )


def test_kill_switch_controls_every_review_path_after_checkout() -> None:
    workflow = _text(REVIEW_WORKFLOW)

    checkout = workflow.index("- name: Checkout repository")
    kill_switch = workflow.index("- name: Check Workflow Kill Switch")
    review = workflow.index("- name: Run Claude Code Review")

    assert checkout < kill_switch < review
    assert "id: kill-switch" in workflow
    assert workflow.count("steps.kill-switch.outputs.disabled != 'true'") >= 6


def test_incomplete_review_is_a_failing_gate() -> None:
    workflow = _text(REVIEW_WORKFLOW)

    assert "github.event.pull_request.author_association" in workflow
    for association in ("OWNER", "MEMBER", "COLLABORATOR"):
        assert association in workflow
    assert "pull-requests: write" in workflow
    assert "issues: write" in workflow
    assert "Fail when automated review did not complete" in workflow
    assert "Automated review is an enforced gate and did not complete." in workflow


def test_interactive_ai_workflow_requires_trusted_author_association() -> None:
    workflow = _text(CLAUDE_WORKFLOW)

    assert "author_association" in workflow
    for association in ("OWNER", "MEMBER", "COLLABORATOR"):
        assert association in workflow


def test_schema_and_dependency_security_gates_are_blocking() -> None:
    workflow = _text(QUALITY_WORKFLOW)

    assert (
        "check-jsonschema --builtin-schema github-workflows {} + || true"
        not in workflow
    )
    assert 'pip-audit --requirement "$f"' in workflow
    assert 'pip-audit --requirement "$f" || true' not in workflow


def test_write_workflow_keeps_push_credentials_available() -> None:
    workflow = _text(CODEX_SYNC_WORKFLOW)

    assert "persist-credentials: true" in workflow
    assert "token: ${{ github.token }}" in workflow
    commit_step = workflow.split("- name: Commit changes (dev only)", maxsplit=1)[1]
    commit_step = commit_step.split("- name: Warn if main has drift", maxsplit=1)[0]
    assert "token:" not in commit_step


def test_virustotal_pr_diff_uses_merge_base() -> None:
    workflow = _text(VIRUSTOTAL_WORKFLOW)

    base_diff_lines = [
        line.strip()
        for line in workflow.splitlines()
        if line.strip().startswith('"$BASE_SHA')
    ]
    assert len(base_diff_lines) == 1
    assert base_diff_lines[0].startswith('"$BASE_SHA...$HEAD_SHA"')


def test_smart_sync_enablement_is_documented() -> None:
    workflow = _text(SMART_SYNC_WORKFLOW)
    setup = _text(AUTOMATION_SETUP)

    assert "vars.PROJECT_SYNC_ENABLED == 'true'" in workflow
    assert "PROJECT_SYNC_ENABLED=true" in setup
