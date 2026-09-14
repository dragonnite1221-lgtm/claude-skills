"""Regression test for TestSuite.calculate_summary()'s PASS/PARTIAL classification.

A batch made up entirely of PARTIAL scripts (some of their own tests failed,
but zero outright FAILed and zero had NO_TESTS) must be reported -- and
exit -- as PARTIAL, never as a clean PASS. main() derives the process exit
code straight from summary["overall_status"], so this field being wrong
makes CI report success (exit code 0) for a batch that is not fully
passing."""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_TESTER = REPO_ROOT / "engineering" / "skill-tester" / "scripts" / "script_tester.py"

spec = importlib.util.spec_from_file_location("script_tester", SCRIPT_TESTER)
script_tester = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_tester)


def _suite_with_statuses(*statuses):
    suite = script_tester.TestSuite("dummy-skill")
    for i, status in enumerate(statuses):
        result = script_tester.ScriptTestResult(f"script_{i}.py")
        result.overall_status = status
        suite.add_script_result(result)
    suite.calculate_summary()
    return suite


def test_all_partial_batch_is_reported_as_partial():
    suite = _suite_with_statuses("PARTIAL", "PARTIAL")
    got = suite.summary["overall_status"]
    if got != "PARTIAL":
        raise AssertionError(f"expected PARTIAL, got {got}: {suite.summary}")


def test_all_pass_batch_is_reported_as_pass():
    suite = _suite_with_statuses("PASS", "PASS")
    got = suite.summary["overall_status"]
    if got != "PASS":
        raise AssertionError(f"expected PASS, got {got}: {suite.summary}")


def test_mixed_pass_and_partial_is_reported_as_partial():
    suite = _suite_with_statuses("PASS", "PARTIAL")
    got = suite.summary["overall_status"]
    if got != "PARTIAL":
        raise AssertionError(f"expected PARTIAL, got {got}: {suite.summary}")


def test_all_failed_batch_is_reported_as_fail():
    suite = _suite_with_statuses("FAIL", "FAIL")
    got = suite.summary["overall_status"]
    if got != "FAIL":
        raise AssertionError(f"expected FAIL, got {got}: {suite.summary}")


def test_failed_and_partial_mix_is_reported_as_partial():
    suite = _suite_with_statuses("FAIL", "PARTIAL")
    got = suite.summary["overall_status"]
    if got != "PARTIAL":
        raise AssertionError(f"expected PARTIAL, got {got}: {suite.summary}")


# --- CLI exit-code contract (CONVENTIONS.md: 0=success, 1=warnings,
# 2=critical errors) -------------------------------------------------------


def _run_main_with_status(monkeypatch, capsys, overall_status, global_error=None):
    """Run script_tester.main() against a canned TestSuite result, without
    needing real script fixtures on disk, and return the SystemExit code."""
    suite = script_tester.TestSuite("dummy-skill")
    if global_error:
        suite.add_global_error(global_error)
    else:
        suite.add_script_result(_suite_with_statuses(overall_status).script_results["script_0.py"])
        suite.calculate_summary()

    def fake_test_all_scripts(self):
        return suite

    monkeypatch.setattr(script_tester.ScriptTester, "test_all_scripts", fake_test_all_scripts)
    monkeypatch.setattr(sys, "argv", ["script_tester.py", "dummy-skill", "--json"])

    try:
        script_tester.main()
    except SystemExit as exc:
        capsys.readouterr()
        return exc.code
    raise AssertionError("main() did not call sys.exit()")


def test_cli_exits_0_on_pass(monkeypatch, capsys):
    code = _run_main_with_status(monkeypatch, capsys, "PASS")
    assert code == 0, f"expected exit 0 (success) for PASS, got {code}"


def test_cli_exits_1_on_partial(monkeypatch, capsys):
    code = _run_main_with_status(monkeypatch, capsys, "PARTIAL")
    assert code == 1, f"expected exit 1 (warning) for PARTIAL, got {code}"


def test_cli_exits_2_on_fail(monkeypatch, capsys):
    code = _run_main_with_status(monkeypatch, capsys, "FAIL")
    assert code == 2, f"expected exit 2 (critical) for FAIL, got {code}"


def test_cli_exits_2_on_global_error(monkeypatch, capsys):
    code = _run_main_with_status(monkeypatch, capsys, None, global_error="No scripts directory found")
    assert code == 2, f"expected exit 2 (critical) for a global error, got {code}"
