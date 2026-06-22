# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dry_run_base import *  # noqa: F403,E402


PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"
WARN = "\033[33m!\033[0m"
class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.details = []

    def ok(self, msg):
        self.passed += 1
        self.details.append((PASS, msg))

    def fail(self, msg):
        self.failed += 1
        self.details.append((FAIL, msg))

    def warn(self, msg):
        self.warnings += 1
        self.details.append((WARN, msg))

    def print(self, verbose=False):
        if verbose:
            for icon, msg in self.details:
                print(f"  {icon} {msg}")
            print()
        total = self.passed + self.failed
        status = "PASS" if self.failed == 0 else "FAIL"
        color = "\033[32m" if self.failed == 0 else "\033[31m"
        warn_str = f", {self.warnings} warnings" if self.warnings else ""
        print(f"{color}{status}\033[0m  {self.passed}/{total} checks passed{warn_str}")
        return self.failed == 0
def rel(path):
    """Path relative to plugin root for display."""
    return os.path.relpath(path, PLUGIN_ROOT)
def check_json(results):
    """Validate settings.json and plugin.json."""
    json_files = [
        os.path.join(PLUGIN_ROOT, "settings.json"),
        os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"),
    ]
    for path in json_files:
        name = rel(path)
        if not os.path.exists(path):
            results.fail(f"{name} — file missing")
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            results.ok(f"{name} — valid JSON")
        except json.JSONDecodeError as e:
            results.fail(f"{name} — invalid JSON: {e}")
            continue

        # plugin.json: only allowed fields
        if name.endswith("plugin.json"):
            allowed = {"name", "description", "version", "author", "homepage",
                       "repository", "license", "skills"}
            extra = set(data.keys()) - allowed
            if extra:
                results.fail(f"{name} — disallowed fields: {extra}")
            else:
                results.ok(f"{name} — schema fields OK")

    # Cross-check versions
    try:
        with open(json_files[0]) as f:
            v1 = json.load(f).get("version")
        with open(json_files[1]) as f:
            v2 = json.load(f).get("version")
        if v1 and v2 and v1 == v2:
            results.ok(f"version match ({v1})")
        elif v1 and v2:
            results.fail(f"version mismatch: settings={v1}, plugin={v2}")
    except Exception:
        pass
FRONTMATTER_RE = re.compile(r"^---\n(.+?)\n---", re.DOTALL)
REQUIRED_FM_KEYS = {"name", "description"}
def check_frontmatter(results):
    """Validate YAML frontmatter in all SKILL.md files."""
    skill_files = []
    for root, _dirs, files in os.walk(PLUGIN_ROOT):
        for f in files:
            if f == "SKILL.md":
                skill_files.append(os.path.join(root, f))

    for path in skill_files:
        name = rel(path)
        with open(path) as f:
            content = f.read()
        m = FRONTMATTER_RE.match(content)
        if not m:
            results.fail(f"{name} — missing YAML frontmatter")
            continue
        # Lightweight key check (no PyYAML dependency)
        fm_text = m.group(1)
        found_keys = set()
        for line in fm_text.splitlines():
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                found_keys.add(key)
        missing = REQUIRED_FM_KEYS - found_keys
        if missing:
            results.fail(f"{name} — frontmatter missing keys: {missing}")
        else:
            results.ok(f"{name} — frontmatter OK")
