# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from frontend_scaffolder_base import *  # noqa: F403,E402


TEMPLATES = {
    "nextjs": {
        "name": "Next.js 14+ App Router",
        "description": "Modern Next.js with App Router, Server Components, and TypeScript",
        "structure": {
            "app": {
                "layout.tsx": "ROOT_LAYOUT",
                "page.tsx": "HOME_PAGE",
                "globals.css": "GLOBALS_CSS",
                "(auth)": {
                    "login": {"page.tsx": "AUTH_PAGE"},
                    "register": {"page.tsx": "AUTH_PAGE"},
                },
                "api": {
                    "health": {"route.ts": "HEALTH_ROUTE"},
                },
            },
            "components": {
                "ui": {
                    "button.tsx": "UI_BUTTON",
                    "input.tsx": "UI_INPUT",
                    "card.tsx": "UI_CARD",
                    "index.ts": "UI_INDEX",
                },
                "layout": {
                    "header.tsx": "LAYOUT_HEADER",
                    "footer.tsx": "LAYOUT_FOOTER",
                    "sidebar.tsx": "LAYOUT_SIDEBAR",
                },
            },
            "lib": {
                "utils.ts": "UTILS",
                "constants.ts": "CONSTANTS",
            },
            "hooks": {
                "use-debounce.ts": "HOOK_DEBOUNCE",
                "use-local-storage.ts": "HOOK_LOCAL_STORAGE",
            },
            "types": {
                "index.ts": "TYPES_INDEX",
            },
            "public": {
                ".gitkeep": "EMPTY",
            },
        },
        "config_files": [
            "next.config.js",
            "tailwind.config.ts",
            "tsconfig.json",
            "postcss.config.js",
            ".eslintrc.json",
            ".prettierrc",
            ".gitignore",
            "package.json",
        ],
    },
    "react": {
        "name": "React + Vite",
        "description": "Modern React with Vite, TypeScript, and Tailwind CSS",
        "structure": {
            "src": {
                "App.tsx": "REACT_APP",
                "main.tsx": "REACT_MAIN",
                "index.css": "GLOBALS_CSS",
                "components": {
                    "ui": {
                        "button.tsx": "UI_BUTTON",
                        "input.tsx": "UI_INPUT",
                        "card.tsx": "UI_CARD",
                        "index.ts": "UI_INDEX",
                    },
                },
                "hooks": {
                    "use-debounce.ts": "HOOK_DEBOUNCE",
                    "use-local-storage.ts": "HOOK_LOCAL_STORAGE",
                },
                "lib": {
                    "utils.ts": "UTILS",
                },
                "types": {
                    "index.ts": "TYPES_INDEX",
                },
            },
            "public": {
                ".gitkeep": "EMPTY",
            },
        },
        "config_files": [
            "vite.config.ts",
            "tailwind.config.ts",
            "tsconfig.json",
            "postcss.config.js",
            ".eslintrc.json",
            ".prettierrc",
            ".gitignore",
            "package.json",
            "index.html",
        ],
    },
}
