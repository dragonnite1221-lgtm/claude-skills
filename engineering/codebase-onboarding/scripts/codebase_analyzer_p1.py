# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402


IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "venv",
    ".venv",
    "__pycache__",
}
EXT_TO_LANG = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++",
    ".swift": "Swift",
    ".sql": "SQL",
    ".sh": "Shell",
}
KEY_CONFIG_FILES = [
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    "nx.json",
    "lerna.json",
    "tsconfig.json",
    "next.config.js",
    "next.config.mjs",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "docker-compose.yml",
    "Dockerfile",
    ".github/workflows",
]
def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.is_file():
                yield path
def detect_languages(paths: Iterable[Path]) -> Dict[str, int]:
    counts: Counter[str] = Counter()
    for path in paths:
        lang = EXT_TO_LANG.get(path.suffix.lower())
        if lang:
            counts[lang] += 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))
def find_key_configs(root: Path) -> List[str]:
    found: List[str] = []
    for rel in KEY_CONFIG_FILES:
        if (root / rel).exists():
            found.append(rel)
    return found
def top_level_structure(root: Path, max_depth: int) -> List[str]:
    lines: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        depth = 0 if str(rel) == "." else len(rel.parts)
        if depth > max_depth:
            dirnames[:] = []
            continue

        if any(part in IGNORED_DIRS for part in rel.parts):
            dirnames[:] = []
            continue

        indent = "  " * depth
        if str(rel) != ".":
            lines.append(f"{indent}{rel.name}/")

        visible_files = [f for f in sorted(filenames) if not f.startswith(".")]
        for filename in visible_files[:10]:
            lines.append(f"{indent}  {filename}")

        dirnames[:] = sorted([d for d in dirnames if d not in IGNORED_DIRS])
    return lines
def build_report(root: Path, max_depth: int) -> Dict[str, object]:
    files = list(iter_files(root))
    languages = detect_languages(files)
    total_files = len(files)
    file_count_by_ext: Counter[str] = Counter(p.suffix.lower() or "<no-ext>" for p in files)

    largest = sorted(
        ((str(p.relative_to(root)), p.stat().st_size) for p in files),
        key=lambda item: item[1],
        reverse=True,
    )[:20]

    return {
        "root": str(root),
        "file_count": total_files,
        "languages": languages,
        "key_config_files": find_key_configs(root),
        "top_extensions": dict(file_count_by_ext.most_common(12)),
        "largest_files": largest,
        "directory_structure": top_level_structure(root, max_depth),
    }
def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{num_bytes}B"
