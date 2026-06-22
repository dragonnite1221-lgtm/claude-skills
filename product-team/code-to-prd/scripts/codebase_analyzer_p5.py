# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402
# fmt: off
from codebase_analyzer_p1 import API_DIR_PATTERNS, CONTROLLER_DIR_PATTERNS, DTO_DIR_PATTERNS, I18N_DIR_PATTERNS, MODEL_DIR_PATTERNS, ROUTE_DIR_PATTERNS, STATE_DIR_PATTERNS  # noqa: E402,E501
from codebase_analyzer_p2 import detect_framework, extract_routes_from_file, extract_routes_from_filesystem, find_dirs, walk_files  # noqa: E402,E501
from codebase_analyzer_p3 import extract_apis_from_file, extract_backend_routes, extract_enums  # noqa: E402,E501
from codebase_analyzer_p4 import count_components, extract_models  # noqa: E402,E501
# fmt: on


def analyze_project(project_root: Path) -> Dict[str, Any]:
    """Run full analysis on a frontend project."""
    root = Path(project_root).resolve()
    if not root.is_dir():
        return {"error": f"Not a directory: {root}"}

    # 1. Framework detection
    framework_info = detect_framework(root)

    # 2. File inventory
    all_files = walk_files(root)
    component_counts = count_components(all_files)

    # 3. Directory structure
    route_dirs = find_dirs(root, ROUTE_DIR_PATTERNS)
    api_dirs = find_dirs(root, API_DIR_PATTERNS)
    state_dirs = find_dirs(root, STATE_DIR_PATTERNS)
    i18n_dirs = find_dirs(root, I18N_DIR_PATTERNS)

    # 4. Routes (frontend + backend)
    routes = []
    fw = framework_info["framework"]

    # Frontend: config-based routes
    for f in all_files:
        if any(p in f.name.lower() for p in ["router", "routes", "routing"]):
            routes.extend(extract_routes_from_file(f))

    # Frontend: file-system routes (Next.js, Nuxt, SvelteKit)
    if fw in ("next", "nuxt", "sveltekit", "remix", "astro"):
        for d in route_dirs:
            routes.extend(extract_routes_from_filesystem(d, root))

    # Backend: NestJS controllers, Django urls
    if fw in ("nestjs", "express", "fastify", "django"):
        for f in all_files:
            if fw == "django" and "urls.py" in f.name:
                routes.extend(extract_backend_routes(f, fw))
            elif fw in ("nestjs", "express", "fastify") and ".controller." in f.name:
                routes.extend(extract_backend_routes(f, fw))

    # Deduplicate routes by path (+ method for backend)
    seen_paths: Set[str] = set()
    unique_routes = []
    for r in routes:
        key = r["path"] if r.get("type") != "backend" else f"{r.get('method', '')}:{r['path']}"
        if key not in seen_paths:
            seen_paths.add(key)
            unique_routes.append(r)
    routes = sorted(unique_routes, key=lambda r: r["path"])

    # 5. API calls
    apis = []
    for f in all_files:
        apis.extend(extract_apis_from_file(f))

    # Deduplicate APIs by path+method
    seen_apis: Set[Tuple[str, str]] = set()
    unique_apis = []
    for a in apis:
        key = (a["path"], a["method"])
        if key not in seen_apis:
            seen_apis.add(key)
            unique_apis.append(a)
    apis = sorted(unique_apis, key=lambda a: a["path"])

    # 6. Enums
    enums = []
    for f in all_files:
        enums.extend(extract_enums(f))

    # 7. Models/entities (backend)
    models = []
    if fw in ("django", "fastapi", "flask", "nestjs"):
        for f in all_files:
            if fw == "django" and "models.py" in f.name:
                models.extend(extract_models(f, fw))
            elif fw == "nestjs" and (".entity." in f.name or ".dto." in f.name):
                models.extend(extract_models(f, fw))

    # Deduplicate models by name
    seen_models: Set[str] = set()
    unique_models = []
    for m in models:
        if m["name"] not in seen_models:
            seen_models.add(m["name"])
            unique_models.append(m)
    models = sorted(unique_models, key=lambda m: m["name"])

    # Backend-specific directories
    controller_dirs = find_dirs(root, CONTROLLER_DIR_PATTERNS)
    model_dirs = find_dirs(root, MODEL_DIR_PATTERNS)
    dto_dirs = find_dirs(root, DTO_DIR_PATTERNS)

    # 8. Summary
    mock_count = sum(1 for a in apis if a.get("mock_detected"))
    real_count = sum(1 for a in apis if a.get("integrated"))
    backend_routes = [r for r in routes if r.get("type") == "backend"]
    frontend_routes = [r for r in routes if r.get("type") != "backend"]

    analysis = {
        "project": {
            "root": str(root),
            "name": framework_info.get("name", root.name),
            "framework": framework_info["framework"],
            "detected_frameworks": framework_info.get("detected_frameworks", []),
            "key_dependencies": framework_info.get("key_deps", {}),
            "stack_type": "backend" if fw in ("django", "fastapi", "flask", "nestjs", "express", "fastify") and not frontend_routes else
                          "fullstack" if backend_routes and frontend_routes else "frontend",
        },
        "structure": {
            "total_files": len(all_files),
            "components": component_counts,
            "route_dirs": [str(d) for d in route_dirs],
            "api_dirs": [str(d) for d in api_dirs],
            "state_dirs": [str(d) for d in state_dirs],
            "i18n_dirs": [str(d) for d in i18n_dirs],
            "controller_dirs": [str(d) for d in controller_dirs],
            "model_dirs": [str(d) for d in model_dirs],
            "dto_dirs": [str(d) for d in dto_dirs],
        },
        "routes": {
            "count": len(routes),
            "frontend_pages": frontend_routes,
            "backend_endpoints": backend_routes,
            "pages": routes,  # backward compat
        },
        "apis": {
            "total": len(apis),
            "integrated": real_count,
            "mock": mock_count,
            "endpoints": apis,
        },
        "enums": {
            "count": len(enums),
            "definitions": enums,
        },
        "models": {
            "count": len(models),
            "definitions": models,
        },
        "summary": {
            "pages": len(frontend_routes),
            "backend_endpoints": len(backend_routes),
            "api_endpoints": len(apis),
            "api_integrated": real_count,
            "api_mock": mock_count,
            "enums": len(enums),
            "models": len(models),
            "has_i18n": len(i18n_dirs) > 0,
            "has_state_management": len(state_dirs) > 0,
            "stack_type": "backend" if fw in ("django", "fastapi", "flask", "nestjs", "express", "fastify") and not frontend_routes else
                          "fullstack" if backend_routes and frontend_routes else "frontend",
        },
    }

    return analysis
