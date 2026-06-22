# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_bootstrapper_base import *  # noqa: F403,E402
# fmt: off
from project_bootstrapper_p2 import generate_db_service, generate_redis_service  # noqa: E402,E501
# fmt: on


def generate_docker_compose(config: Dict[str, Any]) -> str:
    """Generate docker-compose.yml."""
    name = config.get("name", "app")
    stack = config.get("stack", "nextjs")
    db = config.get("database", "postgresql")

    services = {
        "app": {
            "build": ".",
            "ports": ["3000:3000"],
            "env_file": [".env"],
            "depends_on": ["db"] if db else [],
            "volumes": [".:/app", "/app/node_modules"] if stack != "fastapi" else [".:/app"]
        }
    }

    if db == "postgresql":
        services["db"] = {
            "image": "postgres:16-alpine",
            "ports": ["5432:5432"],
            "environment": {
                "POSTGRES_USER": "user",
                "POSTGRES_PASSWORD": "password",
                "POSTGRES_DB": "mydb"
            },
            "volumes": ["pgdata:/var/lib/postgresql/data"]
        }
    elif db == "mongodb":
        services["db"] = {
            "image": "mongo:7",
            "ports": ["27017:27017"],
            "volumes": ["mongodata:/data/db"]
        }

    if config.get("features", {}).get("redis"):
        services["redis"] = {
            "image": "redis:7-alpine",
            "ports": ["6379:6379"]
        }

    compose = {
        "version": "3.8",
        "services": services,
        "volumes": {}
    }
    if db == "postgresql":
        compose["volumes"]["pgdata"] = {}
    elif db == "mongodb":
        compose["volumes"]["mongodata"] = {}

    # Manual YAML-like output (avoid pyyaml dependency)
    nl = "\n"
    depends_on = f"    depends_on:{nl}      - db" if db else ""
    vol_line = "  pgdata:" if db == "postgresql" else "  mongodata:" if db == "mongodb" else "  {}"
    return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    env_file:
      - .env
    volumes:
      - .:/app
{depends_on}

{generate_db_service(db)}
{generate_redis_service(config)}
volumes:
{vol_line}
"""
def generate_gitignore(stack: str) -> str:
    """Generate .gitignore."""
    common = "node_modules/\n.env\n.env.local\ndist/\nbuild/\n.next/\n*.log\n.DS_Store\ncoverage/\n__pycache__/\n*.pyc\n.pytest_cache/\n.venv/\n"
    return common
def generate_dockerfile(config: Dict[str, Any]) -> str:
    """Generate Dockerfile."""
    stack = config.get("stack", "nextjs")
    if stack == "fastapi":
        return """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
"""
    return """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
"""
