# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from frontend_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from frontend_scaffolder_p2 import FEATURES  # noqa: E402,E501
from frontend_scaffolder_p7 import _mod_cg1_0  # noqa: E402,E501
# fmt: on


def _mod_cg1_1():
    return {
        ".prettierrc": '''{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
''',
        ".gitignore": '''# Dependencies
node_modules/
.pnp
.pnp.js

# Build
.next/
out/
dist/
build/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
''',
        "index.html": '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>''' + name + '''</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
    }
def get_config_templates(name: str, template: str, features: List[str]) -> Dict[str, str]:
    """Get configuration file contents."""
    deps = {
        "nextjs": {
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.0.0",
            },
            "devDependencies": {
                "@types/node": "^20.0.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "autoprefixer": "^10.0.0",
                "eslint": "^8.0.0",
                "eslint-config-next": "^14.0.0",
                "postcss": "^8.0.0",
                "prettier": "^3.0.0",
                "tailwindcss": "^3.4.0",
                "typescript": "^5.0.0",
            },
        },
        "react": {
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.0.0",
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.0.0",
                "autoprefixer": "^10.0.0",
                "eslint": "^8.0.0",
                "postcss": "^8.0.0",
                "prettier": "^3.0.0",
                "tailwindcss": "^3.4.0",
                "typescript": "^5.0.0",
                "vite": "^5.0.0",
            },
        },
    }

    # Add feature dependencies
    for feature in features:
        if feature in FEATURES:
            for dep in FEATURES[feature].get("dependencies", []):
                deps[template]["dependencies"][dep] = "latest"

    package_json = {
        "name": name,
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev" if template == "nextjs" else "vite",
            "build": "next build" if template == "nextjs" else "vite build",
            "start": "next start" if template == "nextjs" else "vite preview",
            "lint": "eslint . --ext .ts,.tsx",
            "format": "prettier --write .",
        },
        "dependencies": deps[template]["dependencies"],
        "devDependencies": deps[template]["devDependencies"],
    }

    return {**_mod_cg1_0(), **_mod_cg1_1()}
