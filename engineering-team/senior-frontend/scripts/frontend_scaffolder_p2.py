# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from frontend_scaffolder_base import *  # noqa: F403,E402


FEATURES = {
    "auth": {
        "description": "Authentication with session management",
        "files": {
            "lib/auth.ts": "AUTH_LIB",
            "middleware.ts": "AUTH_MIDDLEWARE",
            "components/auth/login-form.tsx": "LOGIN_FORM",
            "components/auth/register-form.tsx": "REGISTER_FORM",
        },
        "dependencies": ["next-auth", "@auth/core"],
    },
    "api": {
        "description": "API client with React Query",
        "files": {
            "lib/api-client.ts": "API_CLIENT",
            "lib/query-client.ts": "QUERY_CLIENT",
            "providers/query-provider.tsx": "QUERY_PROVIDER",
        },
        "dependencies": ["@tanstack/react-query", "axios"],
    },
    "forms": {
        "description": "Form handling with React Hook Form + Zod",
        "files": {
            "lib/form-utils.ts": "FORM_UTILS",
            "components/forms/form-field.tsx": "FORM_FIELD",
        },
        "dependencies": ["react-hook-form", "@hookform/resolvers", "zod"],
    },
    "testing": {
        "description": "Testing setup with Vitest and Testing Library",
        "files": {
            "vitest.config.ts": "VITEST_CONFIG",
            "src/test/setup.ts": "TEST_SETUP",
            "src/test/utils.tsx": "TEST_UTILS",
        },
        "dependencies": ["vitest", "@testing-library/react", "@testing-library/jest-dom"],
    },
    "storybook": {
        "description": "Component documentation with Storybook",
        "files": {
            ".storybook/main.ts": "STORYBOOK_MAIN",
            ".storybook/preview.ts": "STORYBOOK_PREVIEW",
        },
        "dependencies": ["@storybook/react-vite", "@storybook/addon-essentials"],
    },
}
