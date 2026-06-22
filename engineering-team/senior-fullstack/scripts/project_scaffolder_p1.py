# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_scaffolder_base import *  # noqa: F403,E402


TEMPLATES = {
    "nextjs": {
        "name": "Next.js Full Stack",
        "description": "Next.js 14+ with App Router, TypeScript, Tailwind CSS",
        "structure": {
            "src/app": ["layout.tsx", "page.tsx", "globals.css", "api/health/route.ts"],
            "src/components/ui": ["Button.tsx", "Card.tsx", "Input.tsx"],
            "src/components/layout": ["Header.tsx", "Footer.tsx"],
            "src/lib": ["utils.ts", "db.ts"],
            "src/types": ["index.ts"],
            "public": [],
            "": ["package.json", "tsconfig.json", "tailwind.config.ts", "next.config.js",
                 ".env.example", ".gitignore", "README.md"]
        }
    },
    "fastapi-react": {
        "name": "FastAPI + React",
        "description": "FastAPI backend with React frontend, PostgreSQL",
        "structure": {
            "backend/app": ["__init__.py", "main.py", "config.py", "database.py"],
            "backend/app/api": ["__init__.py", "routes.py", "deps.py"],
            "backend/app/models": ["__init__.py", "user.py"],
            "backend/app/schemas": ["__init__.py", "user.py"],
            "backend": ["requirements.txt", "alembic.ini", "Dockerfile"],
            "frontend/src": ["App.tsx", "main.tsx", "index.css"],
            "frontend/src/components": ["Layout.tsx"],
            "frontend/src/hooks": ["useApi.ts"],
            "frontend": ["package.json", "tsconfig.json", "vite.config.ts", "Dockerfile"],
            "": ["docker-compose.yml", ".env.example", ".gitignore", "README.md"]
        }
    },
    "mern": {
        "name": "MERN Stack",
        "description": "MongoDB, Express, React, Node.js with TypeScript",
        "structure": {
            "server/src": ["index.ts", "config.ts", "database.ts"],
            "server/src/routes": ["index.ts", "users.ts"],
            "server/src/models": ["User.ts"],
            "server/src/middleware": ["auth.ts", "error.ts"],
            "server": ["package.json", "tsconfig.json", "Dockerfile"],
            "client/src": ["App.tsx", "main.tsx"],
            "client/src/components": ["Layout.tsx"],
            "client/src/services": ["api.ts"],
            "client": ["package.json", "tsconfig.json", "vite.config.ts", "Dockerfile"],
            "": ["docker-compose.yml", ".env.example", ".gitignore", "README.md"]
        }
    },
    "django-react": {
        "name": "Django + React",
        "description": "Django REST Framework backend with React frontend",
        "structure": {
            "backend/config": ["__init__.py", "settings.py", "urls.py", "wsgi.py"],
            "backend/apps/users": ["__init__.py", "models.py", "serializers.py", "views.py", "urls.py"],
            "backend": ["manage.py", "requirements.txt", "Dockerfile"],
            "frontend/src": ["App.tsx", "main.tsx"],
            "frontend/src/components": ["Layout.tsx"],
            "frontend": ["package.json", "tsconfig.json", "vite.config.ts", "Dockerfile"],
            "": ["docker-compose.yml", ".env.example", ".gitignore", "README.md"]
        }
    }
}
