# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from init_vault_base import *  # noqa: F403,E402


SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PLUGIN_DIR / "assets"
VAULT_DIRS = [
    "raw",
    "raw/assets",
    "wiki",
    "wiki/entities",
    "wiki/concepts",
    "wiki/sources",
    "wiki/comparisons",
    "wiki/synthesis",
]
TOOL_FILES = {
    "claude-code": ["CLAUDE.md.template:CLAUDE.md"],
    "codex": ["AGENTS.md.template:AGENTS.md"],
    "cursor": ["AGENTS.md.template:AGENTS.md", "cursorrules.template:.cursorrules"],
    "antigravity": ["AGENTS.md.template:AGENTS.md"],
    "opencode": ["AGENTS.md.template:AGENTS.md"],
    "gemini-cli": ["AGENTS.md.template:AGENTS.md"],
    "all": [
        "CLAUDE.md.template:CLAUDE.md",
        "AGENTS.md.template:AGENTS.md",
        "cursorrules.template:.cursorrules",
    ],
}
def render_template(src, dest, variables):
    """Render a template file with {{VAR}} substitutions to dest."""
    if not src.exists():
        print(f"[warn] template missing: {src}", file=sys.stderr)
        return False
    try:
        text = src.read_text(encoding="utf-8")
    except OSError as e:
        print(f"[warn] could not read {src}: {e}", file=sys.stderr)
        return False
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    try:
        dest.write_text(text, encoding="utf-8")
    except OSError as e:
        print(f"[warn] could not write {dest}: {e}", file=sys.stderr)
        return False
    return True
def _error(message, as_json=False):
    if as_json:
        print(json.dumps({"status": "error", "message": message}))
    else:
        print(f"[error] {message}", file=sys.stderr)
    sys.exit(1)
