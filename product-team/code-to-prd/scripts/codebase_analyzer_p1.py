# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402


IGNORED_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage",
    "venv", ".venv", "__pycache__", ".nuxt", ".output", ".cache",
    ".turbo", ".vercel", "out", "storybook-static",
    ".tox", ".mypy_cache", ".pytest_cache", "htmlcov", "staticfiles",
    "media", "migrations", "egg-info",
}
FRAMEWORK_SIGNALS = {
    "react": ["react", "react-dom"],
    "next": ["next"],
    "vue": ["vue"],
    "nuxt": ["nuxt"],
    "angular": ["@angular/core"],
    "svelte": ["svelte"],
    "sveltekit": ["@sveltejs/kit"],
    "solid": ["solid-js"],
    "astro": ["astro"],
    "remix": ["@remix-run/react"],
    "nestjs": ["@nestjs/core"],
    "express": ["express"],
    "fastify": ["fastify"],
}
PYTHON_FRAMEWORK_FILES = {
    "django": ["manage.py", "settings.py"],
    "fastapi": ["main.py"],  # confirmed via imports
    "flask": ["app.py"],      # confirmed via imports
}
ROUTE_FILE_PATTERNS = [
    "**/router.{ts,tsx,js,jsx}",
    "**/routes.{ts,tsx,js,jsx}",
    "**/routing.{ts,tsx,js,jsx}",
    "**/app-routing*.{ts,tsx,js,jsx}",
]
ROUTE_DIR_PATTERNS = [
    "pages", "views", "routes", "app",
    "src/pages", "src/views", "src/routes", "src/app",
]
API_DIR_PATTERNS = [
    "api", "services", "requests", "endpoints", "client",
    "src/api", "src/services", "src/requests",
]
STATE_DIR_PATTERNS = [
    "store", "stores", "models", "context", "state",
    "src/store", "src/stores", "src/models", "src/context",
]
I18N_DIR_PATTERNS = [
    "locales", "i18n", "lang", "translations", "messages",
    "src/locales", "src/i18n", "src/lang",
]
CONTROLLER_DIR_PATTERNS = [
    "controllers", "src/controllers", "src/modules",
]
MODEL_DIR_PATTERNS = [
    "models", "entities", "src/entities", "src/models",
]
DTO_DIR_PATTERNS = [
    "dto", "dtos", "src/dto", "serializers",
]
MOCK_SIGNALS = [
    r"setTimeout\s*\(.*\breturn\b",
    r"Promise\.resolve\s*\(",
    r"\.mock\.",
    r"__mocks__",
    r"mockData",
    r"mock[A-Z]",
    r"faker\.",
    r"fixtures?/",
]
REAL_API_SIGNALS = [
    r"\baxios\b",
    r"\bfetch\s*\(",
    r"httpGet|httpPost|httpPut|httpDelete|httpPatch",
    r"\.get\s*\(\s*['\"`/]",
    r"\.post\s*\(\s*['\"`/]",
    r"\.put\s*\(\s*['\"`/]",
    r"\.delete\s*\(\s*['\"`/]",
    r"\.patch\s*\(\s*['\"`/]",
    r"useSWR|useQuery|useMutation",
    r"\$http\.",
    r"this\.http\.",
]
ROUTE_PATTERNS = [
    # React Router
    r'<Route\s+[^>]*path\s*=\s*["\']([^"\']+)["\']',
    r'path\s*:\s*["\']([^"\']+)["\']',
    # Vue Router
    r'path\s*:\s*["\']([^"\']+)["\']',
    # Angular
    r'path\s*:\s*["\']([^"\']+)["\']',
]
API_PATH_PATTERNS = [
    r'["\'](?:GET|POST|PUT|DELETE|PATCH)["\'].*?["\'](/[a-zA-Z0-9/_\-:{}]+)["\']',
    r'(?:get|post|put|delete|patch)\s*\(\s*["\'](/[a-zA-Z0-9/_\-:{}]+)["\']',
    r'(?:url|path|endpoint|baseURL)\s*[:=]\s*["\'](/[a-zA-Z0-9/_\-:{}]+)["\']',
    r'fetch\s*\(\s*[`"\'](?:https?://[^/]+)?(/[a-zA-Z0-9/_\-:{}]+)',
]
COMPONENT_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".astro"}
CODE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte", ".astro", ".py"}
NEST_ROUTE_PATTERNS = [
    r"@(?:Get|Post|Put|Delete|Patch|Head|Options|All)\s*\(\s*['\"]([^'\"]*)['\"]",
    r"@Controller\s*\(\s*['\"]([^'\"]*)['\"]",
]
DJANGO_ROUTE_PATTERNS = [
    r"path\s*\(\s*['\"]([^'\"]+)['\"]",
    r"url\s*\(\s*r?['\"]([^'\"]+)['\"]",
    r"register\s*\(\s*r?['\"]([^'\"]+)['\"]",
]
PYTHON_MODEL_PATTERNS = [
    r"class\s+(\w+)\s*\(.*?models\.Model\)",
    r"class\s+(\w+)\s*\(.*?BaseModel\)",  # Pydantic
]
NEST_MODEL_PATTERNS = [
    r"@Entity\s*\(.*?\)\s*(?:export\s+)?class\s+(\w+)",
    r"class\s+(\w+(?:Dto|DTO|Entity|Schema))\b",
]
