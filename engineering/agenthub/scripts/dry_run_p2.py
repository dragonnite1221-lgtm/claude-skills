# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dry_run_base import *  # noqa: F403,E402
# fmt: off
from dry_run_p1 import PLUGIN_ROOT, rel  # noqa: E402,E501
# fmt: on


def check_markdown(results):
    """Check for broken code fences and table rows in all .md files."""
    md_files = []
    for root, _dirs, files in os.walk(PLUGIN_ROOT):
        for f in files:
            if f.endswith(".md"):
                md_files.append(os.path.join(root, f))

    for path in md_files:
        name = rel(path)
        with open(path) as f:
            lines = f.readlines()

        # Code fences must be balanced
        fence_count = sum(1 for ln in lines if ln.strip().startswith("```"))
        if fence_count % 2 != 0:
            results.fail(f"{name} — unbalanced code fences ({fence_count} found)")
        else:
            results.ok(f"{name} — code fences balanced")

        # Tables: rows inside a table should have consistent pipe count
        in_table = False
        table_pipes = 0
        table_ok = True
        for i, ln in enumerate(lines, 1):
            stripped = ln.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                pipes = stripped.count("|")
                if not in_table:
                    in_table = True
                    table_pipes = pipes
                elif pipes != table_pipes:
                    # Separator rows (|---|---| ) can differ slightly; skip
                    if not re.match(r"^\|[\s\-:|]+\|$", stripped):
                        results.warn(f"{name}:{i} — table column count mismatch ({pipes} vs {table_pipes})")
                        table_ok = False
            else:
                in_table = False
                table_pipes = 0
def check_scripts(results):
    """Verify every Python script exits 0 on --help."""
    scripts_dir = os.path.join(PLUGIN_ROOT, "scripts")
    if not os.path.isdir(scripts_dir):
        results.warn("scripts/ directory not found")
        return

    for fname in sorted(os.listdir(scripts_dir)):
        if not fname.endswith(".py") or fname == "dry_run.py":
            continue
        path = os.path.join(scripts_dir, fname)
        try:
            proc = subprocess.run(
                [sys.executable, path, "--help"],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode == 0:
                results.ok(f"scripts/{fname} --help exits 0")
            else:
                results.fail(f"scripts/{fname} --help exits {proc.returncode}")
        except subprocess.TimeoutExpired:
            results.fail(f"scripts/{fname} --help timed out")
        except Exception as e:
            results.fail(f"scripts/{fname} --help error: {e}")
def check_references(results):
    """Verify that key files referenced in docs actually exist."""
    expected = [
        "settings.json",
        ".claude-plugin/plugin.json",
        "CLAUDE.md",
        "SKILL.md",
        "README.md",
        "agents/hub-coordinator.md",
        "references/agent-templates.md",
        "references/coordination-strategies.md",
        "scripts/hub_init.py",
        "scripts/dag_analyzer.py",
        "scripts/board_manager.py",
        "scripts/result_ranker.py",
        "scripts/session_manager.py",
    ]
    for ref in expected:
        path = os.path.join(PLUGIN_ROOT, ref)
        if os.path.exists(path):
            results.ok(f"{ref} exists")
        else:
            results.fail(f"{ref} — referenced but missing")
def check_cross_domain(results):
    """Verify non-engineering examples exist in key files (the whole point of this update)."""
    checks = [
        ("settings.json", "content-generation"),
        (".claude-plugin/plugin.json", "content drafts"),
        ("CLAUDE.md", "content drafts"),
        ("SKILL.md", "content variation"),
        ("README.md", "content generation"),
        ("skills/run/SKILL.md", "--judge"),
        ("skills/init/SKILL.md", "LLM judge"),
        ("skills/eval/SKILL.md", "narrative"),
        ("skills/board/SKILL.md", "Storytelling"),
        ("skills/status/SKILL.md", "Storytelling"),
        ("references/agent-templates.md", "landing page copy"),
        ("references/coordination-strategies.md", "flesch_score"),
        ("agents/hub-coordinator.md", "qualitative verdict"),
    ]
    for filepath, needle in checks:
        path = os.path.join(PLUGIN_ROOT, filepath)
        if not os.path.exists(path):
            results.fail(f"{filepath} — missing (cannot check cross-domain)")
            continue
        with open(path) as f:
            content = f.read()
        if needle.lower() in content.lower():
            results.ok(f"{filepath} — contains cross-domain example (\"{needle}\")")
        else:
            results.fail(f"{filepath} — missing cross-domain marker \"{needle}\"")
