# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402
# fmt: off
from codebase_analyzer_p1 import API_PATH_PATTERNS, DJANGO_ROUTE_PATTERNS, MOCK_SIGNALS, NEST_ROUTE_PATTERNS, REAL_API_SIGNALS  # noqa: E402,E501
# fmt: on


def extract_apis_from_file(filepath: Path) -> List[Dict[str, Any]]:
    """Extract API calls from a file."""
    apis = []
    try:
        content = filepath.read_text(errors="replace")
    except IOError:
        return apis

    is_mock = any(re.search(p, content) for p in MOCK_SIGNALS)
    is_real = any(re.search(p, content) for p in REAL_API_SIGNALS)

    for pattern in API_PATH_PATTERNS:
        for match in re.finditer(pattern, content):
            path = match.group(1) if match.lastindex else match.group(0)
            if path and len(path) < 200:
                # Try to detect HTTP method
                context = content[max(0, match.start() - 100):match.end()]
                method = "UNKNOWN"
                for m in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    if m.lower() in context.lower():
                        method = m
                        break

                apis.append({
                    "path": path,
                    "method": method,
                    "source": str(filepath),
                    "line": content[:match.start()].count("\n") + 1,
                    "integrated": is_real and not is_mock,
                    "mock_detected": is_mock,
                })
    return apis
def extract_enums(filepath: Path) -> List[Dict[str, Any]]:
    """Extract enum/constant definitions."""
    enums = []
    try:
        content = filepath.read_text(errors="replace")
    except IOError:
        return enums

    # TypeScript enums
    for match in re.finditer(r"enum\s+(\w+)\s*\{([^}]+)\}", content):
        name = match.group(1)
        body = match.group(2)
        values = re.findall(r"(\w+)\s*=\s*['\"]?([^,'\"\n]+)", body)
        enums.append({
            "name": name,
            "type": "enum",
            "values": {k.strip(): v.strip().rstrip(",") for k, v in values},
            "source": str(filepath),
        })

    # Object constant maps (const STATUS_MAP = { ... })
    for match in re.finditer(
        r"(?:const|export\s+const)\s+(\w*(?:MAP|STATUS|TYPE|ENUM|OPTION|ROLE|STATE)\w*)\s*[:=]\s*\{([^}]+)\}",
        content, re.IGNORECASE
    ):
        name = match.group(1)
        body = match.group(2)
        values = re.findall(r"['\"]?(\w+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]", body)
        if values:
            enums.append({
                "name": name,
                "type": "constant_map",
                "values": dict(values),
                "source": str(filepath),
            })

    return enums
def extract_backend_routes(filepath: Path, framework: str) -> List[Dict[str, str]]:
    """Extract route definitions from NestJS controllers or Django url configs."""
    routes = []
    try:
        content = filepath.read_text(errors="replace")
    except IOError:
        return routes

    patterns = []
    if framework in ("nestjs", "express", "fastify"):
        patterns = NEST_ROUTE_PATTERNS
    elif framework == "django":
        patterns = DJANGO_ROUTE_PATTERNS

    # For NestJS, also grab the controller prefix
    controller_prefix = ""
    if framework == "nestjs":
        m = re.search(r"@Controller\s*\(\s*['\"]([^'\"]*)['\"]", content)
        if m:
            controller_prefix = "/" + m.group(1).strip("/")

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            path = match.group(1)
            if not path or path.startswith("http") or len(path) > 200:
                continue
            # For NestJS method decorators, prepend controller prefix
            if framework == "nestjs" and not path.startswith("/"):
                full_path = f"{controller_prefix}/{path}".replace("//", "/")
            else:
                full_path = path if path.startswith("/") else f"/{path}"

            # Detect HTTP method from decorator name
            method = "UNKNOWN"
            ctx = content[max(0, match.start() - 30):match.start()]
            for m_name in ["Get", "Post", "Put", "Delete", "Patch"]:
                if f"@{m_name}" in ctx or f"@{m_name.lower()}" in ctx:
                    method = m_name.upper()
                    break

            routes.append({
                "path": full_path,
                "method": method,
                "source": str(filepath),
                "line": content[:match.start()].count("\n") + 1,
                "type": "backend",
            })
    return routes
