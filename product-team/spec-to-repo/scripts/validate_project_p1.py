# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from validate_project_base import *  # noqa: F403,E402


MANIFESTS = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "pubspec.yaml",
    "Gemfile",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
]
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb",
    ".dart", ".java", ".kt", ".swift", ".cs", ".cpp", ".c",
}
TEST_PATTERNS = [
    r"test_.*\.py$",
    r".*_test\.py$",
    r".*\.test\.[jt]sx?$",
    r".*\.spec\.[jt]sx?$",
    r".*_test\.go$",
    r".*_test\.rs$",
    r".*_test\.dart$",
    r"test/.*",
    r"tests/.*",
    r"spec/.*",
    r"__tests__/.*",
]
PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bHACK\b",
    r"//\s*implement",
    r"#\s*implement",
    r'raise NotImplementedError',
    r"pass\s*$",
    r"\.\.\.  # placeholder",
]
ENV_VAR_PATTERNS = [
    r"process\.env\.\w+",
    r"os\.environ\[",
    r"os\.getenv\(",
    r"env\(",
    r"std::env::var",
    r"os\.Getenv\(",
    r"ENV\[",
    r"Platform\.environment\[",
]
def find_files(root):
    """Walk directory, skip hidden dirs and common vendor dirs."""
    skip = {".git", "node_modules", ".next", "__pycache__", "target", ".dart_tool",
            "build", "dist", ".venv", "venv", "vendor", ".turbo"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for f in filenames:
            yield os.path.join(dirpath, f)
def check_readme(root):
    path = os.path.join(root, "README.md")
    if not os.path.isfile(path):
        return {"name": "readme", "status": "FAIL", "message": "README.md missing"}
    size = os.path.getsize(path)
    if size < 50:
        return {"name": "readme", "status": "WARN", "message": f"README.md is only {size} bytes — likely incomplete"}
    return {"name": "readme", "status": "PASS", "message": f"README.md exists ({size} bytes)"}
def check_gitignore(root):
    path = os.path.join(root, ".gitignore")
    if not os.path.isfile(path):
        return {"name": "gitignore", "status": "FAIL", "message": ".gitignore missing"}
    return {"name": "gitignore", "status": "PASS", "message": ".gitignore exists"}
def check_env_example(root, all_files):
    uses_env = False
    for filepath in all_files:
        ext = os.path.splitext(filepath)[1]
        if ext not in CODE_EXTENSIONS:
            continue
        try:
            content = open(filepath, "r", encoding="utf-8", errors="ignore").read()
        except (OSError, UnicodeDecodeError):
            continue
        for pattern in ENV_VAR_PATTERNS:
            if re.search(pattern, content):
                uses_env = True
                break
        if uses_env:
            break

    if not uses_env:
        return {"name": "env_example", "status": "PASS", "message": "No env vars detected — .env.example not required"}

    path = os.path.join(root, ".env.example")
    if not os.path.isfile(path):
        return {"name": "env_example", "status": "FAIL", "message": "Code references env vars but .env.example is missing"}
    return {"name": "env_example", "status": "PASS", "message": ".env.example exists"}
def check_no_env_file(root):
    path = os.path.join(root, ".env")
    if os.path.isfile(path):
        return {"name": "no_env_committed", "status": "FAIL", "message": ".env file found — secrets may be committed"}
    return {"name": "no_env_committed", "status": "PASS", "message": "No .env file committed"}
def check_manifest(root):
    for manifest in MANIFESTS:
        if os.path.isfile(os.path.join(root, manifest)):
            return {"name": "manifest", "status": "PASS", "message": f"Package manifest found: {manifest}"}
    return {"name": "manifest", "status": "FAIL", "message": "No package manifest found (package.json, requirements.txt, go.mod, etc.)"}
def check_tests(all_files, root):
    for filepath in all_files:
        rel = os.path.relpath(filepath, root)
        for pattern in TEST_PATTERNS:
            if re.search(pattern, rel):
                return {"name": "tests", "status": "PASS", "message": f"Test file found: {rel}"}
    return {"name": "tests", "status": "FAIL", "message": "No test files found"}
