# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dockerfile_analyzer_base import *  # noqa: F403,E402


ANTI_PATTERNS = [
    {
        "id": "AP001",
        "name": "latest_tag",
        "severity": "high",
        "pattern": r"^FROM\s+\S+:latest",
        "message": "Using :latest tag — pin to a specific version for reproducibility",
        "fix": "Use a specific tag like :3.12-slim or pin by digest",
    },
    {
        "id": "AP002",
        "name": "no_tag",
        "severity": "high",
        "pattern": r"^FROM\s+([a-z][a-z0-9_.-]+)\s*$",
        "message": "No tag specified on base image — defaults to :latest",
        "fix": "Add a specific version tag",
    },
    {
        "id": "AP003",
        "name": "run_apt_no_clean",
        "severity": "medium",
        "pattern": r"^RUN\s+.*apt-get\s+install(?!.*rm\s+-rf\s+/var/lib/apt/lists)",
        "message": "apt-get install without cleanup in same layer — bloats image",
        "fix": "Add && rm -rf /var/lib/apt/lists/* in the same RUN instruction",
    },
    {
        "id": "AP004",
        "name": "run_apk_no_cache",
        "severity": "medium",
        "pattern": r"^RUN\s+.*apk\s+add(?!\s+--no-cache)",
        "message": "apk add without --no-cache — retains package index",
        "fix": "Use: apk add --no-cache <packages>",
    },
    {
        "id": "AP005",
        "name": "add_instead_of_copy",
        "severity": "low",
        "pattern": r"^ADD\s+(?!https?://)\S+",
        "message": "Using ADD for local files — COPY is more explicit and predictable",
        "fix": "Use COPY instead of ADD unless you need tar auto-extraction or URL fetching",
    },
    {
        "id": "AP006",
        "name": "multiple_cmd",
        "severity": "medium",
        "pattern": None,  # Custom check
        "message": "Multiple CMD instructions — only the last one takes effect",
        "fix": "Keep exactly one CMD instruction",
    },
    {
        "id": "AP007",
        "name": "env_secrets",
        "severity": "critical",
        "pattern": r"^(?:ENV|ARG)\s+\S*(?:PASSWORD|SECRET|TOKEN|KEY|API_KEY)\s*=",
        "message": "Secrets in ENV/ARG — baked into image layers and visible in history",
        "fix": "Use BuildKit secrets: RUN --mount=type=secret,id=mytoken",
    },
    {
        "id": "AP008",
        "name": "broad_copy",
        "severity": "medium",
        "pattern": r"^COPY\s+\.\s+\.",
        "message": "COPY . . copies everything — may include secrets, git history, node_modules",
        "fix": "Use .dockerignore and copy specific directories, or copy after dependency install",
    },
    {
        "id": "AP009",
        "name": "no_user",
        "severity": "critical",
        "pattern": None,  # Custom check
        "message": "No USER instruction — container runs as root",
        "fix": "Add USER nonroot or create a dedicated user",
    },
    {
        "id": "AP010",
        "name": "pip_no_cache",
        "severity": "low",
        "pattern": r"^RUN\s+.*pip\s+install(?!\s+--no-cache-dir)",
        "message": "pip install without --no-cache-dir — retains pip cache in layer",
        "fix": "Use: pip install --no-cache-dir -r requirements.txt",
    },
    {
        "id": "AP011",
        "name": "npm_install_dev",
        "severity": "medium",
        "pattern": r"^RUN\s+.*npm\s+install\s*$",
        "message": "npm install includes devDependencies — use npm ci --omit=dev for production",
        "fix": "Use: npm ci --omit=dev (or npm ci --production)",
    },
    {
        "id": "AP012",
        "name": "expose_all",
        "severity": "low",
        "pattern": r"^EXPOSE\s+\d+(?:\s+\d+){3,}",
        "message": "Exposing many ports — only expose what the application actually needs",
        "fix": "Remove unnecessary EXPOSE directives",
    },
    {
        "id": "AP013",
        "name": "curl_wget_without_cleanup",
        "severity": "low",
        "pattern": r"^RUN\s+.*(?:curl|wget)\s+.*(?!&&\s*rm)",
        "message": "Download without cleanup — downloaded archives may remain in layer",
        "fix": "Download, extract, and remove archive in the same RUN instruction",
    },
    {
        "id": "AP014",
        "name": "no_healthcheck",
        "severity": "medium",
        "pattern": None,  # Custom check
        "message": "No HEALTHCHECK instruction — orchestrators can't determine container health",
        "fix": "Add HEALTHCHECK CMD curl -f http://localhost:PORT/health || exit 1",
    },
    {
        "id": "AP015",
        "name": "shell_form_cmd",
        "severity": "low",
        "pattern": r'^(?:CMD|ENTRYPOINT)\s+(?!\[)["\']?\w',
        "message": "Using shell form for CMD/ENTRYPOINT — exec form is preferred for signal handling",
        "fix": 'Use exec form: CMD ["executable", "arg1", "arg2"]',
    },
]
