"""Regression tests for trust boundaries in AI-powered workflows."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_WORKFLOW = ROOT / ".github" / "workflows" / "claude-code-review.yml"
CLAUDE_WORKFLOW = ROOT / ".github" / "workflows" / "claude.yml"
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "ci-quality-gate.yml"
PR_CLOSE_WORKFLOW = ROOT / ".github" / "workflows" / "pr-issue-auto-close.yml"
CODEX_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "sync-codex-skills.yml"
VIRUSTOTAL_WORKFLOW = ROOT / ".github" / "workflows" / "virustotal-scan.yml"
AUTOMATION_SETUP = ROOT / ".github" / "AUTOMATION_SETUP.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_pr_metadata_is_not_interpolated_into_shell_source() -> None:
    workflow = _text(REVIEW_WORKFLOW)

    assert 'PR_TITLE="${{ github.event.pull_request.title }}"' not in workflow
    assert "PR_LABELS: ${{ toJSON(github.event.pull_request.labels.*.name) }}" in workflow


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

    assert "check-jsonschema --builtin-schema github-workflows {} + || true" not in workflow
    assert 'pip-audit --requirement "$f"' in workflow
    assert 'pip-audit --requirement "$f" || true' not in workflow


def test_linked_issue_output_is_not_interpolated_into_javascript() -> None:
    workflow = _text(PR_CLOSE_WORKFLOW)

    assert "const issueNumbers = ${{ steps.extract_issues.outputs.result }};" not in workflow
    assert workflow.count("ISSUE_NUMBERS_JSON: ${{ steps.extract_issues.outputs.result }}") == 3
    assert workflow.count("JSON.parse(process.env.ISSUE_NUMBERS_JSON || '[]')") == 3
    assert workflow.count("Invalid linked-issue output") == 3


def test_issue_close_kill_switch_guards_every_follow_up_step() -> None:
    workflow = _text(PR_CLOSE_WORKFLOW)

    assert "id: kill-switch" in workflow
    assert 'echo "disabled=true" >> "$GITHUB_OUTPUT"' in workflow
    assert 'echo "disabled=false" >> "$GITHUB_OUTPUT"' in workflow
    assert workflow.count("steps.kill-switch.outputs.disabled != 'true'") == 4


def test_codex_sync_push_uses_explicit_ephemeral_authentication() -> None:
    workflow = _text(CODEX_SYNC_WORKFLOW)

    assert "persist-credentials: false" in workflow
    assert "credential.helper" in workflow
    assert "password=\\$GH_TOKEN" in workflow
    assert "GH_TOKEN: ${{ github.token }}" in workflow
    # checkout's token input is supported; the auto-commit action has none.
    assert workflow.count("token: ${{ github.token }}") == 1
    assert "--unset-all credential.helper" in workflow


def test_virustotal_pr_scan_uses_merge_base_diff() -> None:
    workflow = _text(VIRUSTOTAL_WORKFLOW)

    assert '"$BASE_SHA...$HEAD_SHA"' in workflow
    assert '"$BASE_SHA" \\\n+            "$HEAD_SHA"' not in workflow


def test_smart_sync_setup_documents_fail_closed_activation_flag() -> None:
    setup = _text(AUTOMATION_SETUP)

    assert setup.count("PROJECT_SYNC_ENABLED") >= 4
    assert "gh variable list" in setup
    assert "PROJECT_SYNC_ENABLED=true" in setup
