# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402
# fmt: off
from codebase_analyzer_p1 import CODE_EXTENSIONS, FRAMEWORK_SIGNALS, IGNORED_DIRS, ROUTE_PATTERNS  # noqa: E402,E501
# fmt: on


def detect_framework(project_root: Path) -> Dict[str, Any]:
    """Detect framework from package.json (Node.js) or project files (Python)."""
    detected = []
    all_deps = {}
    pkg_name = ""
    pkg_version = ""

    # Node.js detection via package.json
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            with open(pkg_path) as f:
                pkg = json.load(f)
            pkg_name = pkg.get("name", "")
            pkg_version = pkg.get("version", "")
            for key in ("dependencies", "devDependencies", "peerDependencies"):
                all_deps.update(pkg.get(key, {}))
            for framework, signals in FRAMEWORK_SIGNALS.items():
                if any(s in all_deps for s in signals):
                    detected.append(framework)
        except (json.JSONDecodeError, IOError):
            pass

    # Python backend detection via project files and imports
    if (project_root / "manage.py").exists():
        detected.append("django")
    if (project_root / "requirements.txt").exists() or (project_root / "pyproject.toml").exists():
        for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
            req_path = project_root / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text(errors="replace").lower()
                    if "django" in content and "django" not in detected:
                        detected.append("django")
                    if "fastapi" in content:
                        detected.append("fastapi")
                    if "flask" in content and "flask" not in detected:
                        detected.append("flask")
                except IOError:
                    pass

    # Prefer specific over generic
    priority = [
        "sveltekit", "next", "nuxt", "remix", "astro",  # fullstack JS
        "nestjs", "express", "fastify",                   # backend JS
        "django", "fastapi", "flask",                     # backend Python
        "angular", "svelte", "vue", "react", "solid",     # frontend JS
    ]
    framework = "unknown"
    for fw in priority:
        if fw in detected:
            framework = fw
            break

    return {
        "framework": framework,
        "name": pkg_name or project_root.name,
        "version": pkg_version,
        "detected_frameworks": detected,
        "dependency_count": len(all_deps),
        "key_deps": {k: v for k, v in all_deps.items()
                     if any(s in k for s in ["router", "redux", "vuex", "pinia", "zustand",
                                              "mobx", "recoil", "jotai", "tanstack", "swr",
                                              "axios", "tailwind", "material", "ant",
                                              "chakra", "shadcn", "i18n", "intl",
                                              "typeorm", "prisma", "sequelize", "mongoose",
                                              "passport", "jwt", "class-validator"])},
    }
def find_dirs(root: Path, patterns: List[str]) -> List[Path]:
    """Find directories matching common patterns."""
    found = []
    for pattern in patterns:
        candidate = root / pattern
        if candidate.is_dir():
            found.append(candidate)
    return found
def walk_files(root: Path, extensions: Set[str] = CODE_EXTENSIONS) -> List[Path]:
    """Walk project tree, skip ignored dirs, return files matching extensions."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for fname in filenames:
            if Path(fname).suffix in extensions:
                results.append(Path(dirpath) / fname)
    return results
def extract_routes_from_file(filepath: Path) -> List[Dict[str, str]]:
    """Extract route definitions from a file."""
    routes = []
    try:
        content = filepath.read_text(errors="replace")
    except IOError:
        return routes

    for pattern in ROUTE_PATTERNS:
        for match in re.finditer(pattern, content):
            path = match.group(1)
            if path and not path.startswith("http") and len(path) < 200:
                routes.append({
                    "path": path,
                    "source": str(filepath),
                    "line": content[:match.start()].count("\n") + 1,
                })
    return routes
def extract_routes_from_filesystem(pages_dir: Path, root: Path) -> List[Dict[str, str]]:
    """Infer routes from file-system routing (Next.js, Nuxt, SvelteKit)."""
    routes = []
    for filepath in sorted(pages_dir.rglob("*")):
        if filepath.is_file() and filepath.suffix in CODE_EXTENSIONS:
            rel = filepath.relative_to(pages_dir)
            route = "/" + str(rel.with_suffix("")).replace("\\", "/")
            # Normalize index routes
            route = re.sub(r"/index$", "", route) or "/"
            # Convert [param] to :param
            route = re.sub(r"\[\.\.\.(\w+)\]", r"*\1", route)
            route = re.sub(r"\[(\w+)\]", r":\1", route)
            routes.append({
                "path": route,
                "source": str(filepath),
                "filesystem": True,
            })
    return routes
