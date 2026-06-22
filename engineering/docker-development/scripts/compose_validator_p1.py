# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from compose_validator_base import *  # noqa: F403,E402


DEMO_COMPOSE = """
version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:password@db:5432/app
      - SECRET_KEY=my-secret-key
    depends_on:
      - db
      - redis

  db:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: password123
    volumes:
      - ./data:/var/lib/postgresql/data

  redis:
    image: redis
    ports:
      - "6379:6379"

  worker:
    build: .
    command: python worker.py
    environment:
      - DATABASE_URL=postgres://user:password@db:5432/app
"""
def parse_yaml_simple(content):
    """Simple YAML-like parser for docker-compose files (stdlib only).

    Handles the subset of YAML used in typical docker-compose files:
    - Top-level keys
    - Service definitions
    - Lists (- items)
    - Key-value pairs
    - Nested indentation
    """
    result = {"services": {}, "volumes": {}, "networks": {}}
    current_section = None
    current_service = None
    current_key = None
    indent_stack = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level keys
        if indent == 0 and ":" in stripped:
            key = stripped.split(":")[0].strip()
            if key == "services":
                current_section = "services"
            elif key == "volumes":
                current_section = "volumes"
            elif key == "networks":
                current_section = "networks"
            elif key == "version":
                val = stripped.split(":", 1)[1].strip().strip("'\"")
                result["version"] = val
            current_service = None
            current_key = None
            continue

        if current_section == "services":
            # Service name (indent level 2)
            if indent == 2 and ":" in stripped and not stripped.startswith("-"):
                key = stripped.split(":")[0].strip()
                val = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
                if val and not val.startswith("{"):
                    # Simple key:value inside a service
                    if current_service and current_service in result["services"]:
                        result["services"][current_service][key] = val
                    else:
                        current_service = key
                        result["services"][current_service] = {}
                        current_key = None
                else:
                    current_service = key
                    result["services"][current_service] = {}
                    current_key = None
                continue

            if current_service and current_service in result["services"]:
                svc = result["services"][current_service]

                # Service-level keys (indent 4)
                if indent == 4 and ":" in stripped and not stripped.startswith("-"):
                    key = stripped.split(":")[0].strip()
                    val = stripped.split(":", 1)[1].strip()
                    current_key = key
                    if val:
                        svc[key] = val.strip("'\"")
                    else:
                        svc[key] = []
                    continue

                # List items (indent 6 or 8)
                if stripped.startswith("-") and current_key:
                    item = stripped[1:].strip().strip("'\"")
                    if current_key in svc:
                        if isinstance(svc[current_key], list):
                            svc[current_key].append(item)
                        else:
                            svc[current_key] = [svc[current_key], item]
                    else:
                        svc[current_key] = [item]
                    continue

                # Nested key:value under current_key (e.g., healthcheck test)
                if indent >= 6 and ":" in stripped and not stripped.startswith("-"):
                    key = stripped.split(":")[0].strip()
                    val = stripped.split(":", 1)[1].strip()
                    if current_key and current_key in svc:
                        if isinstance(svc[current_key], list):
                            svc[current_key] = {}
                        if isinstance(svc[current_key], dict):
                            svc[current_key][key] = val

    return result
