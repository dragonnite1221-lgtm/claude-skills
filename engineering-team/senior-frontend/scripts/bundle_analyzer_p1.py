# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from bundle_analyzer_base import *  # noqa: F403,E402


HEAVY_PACKAGES = {
    "moment": {
        "size": "290KB",
        "alternative": "date-fns (12KB) or dayjs (2KB)",
        "reason": "Large locale files bundled by default"
    },
    "lodash": {
        "size": "71KB",
        "alternative": "lodash-es with tree-shaking or individual imports (lodash/get)",
        "reason": "Full library often imported when only few functions needed"
    },
    "jquery": {
        "size": "87KB",
        "alternative": "Native DOM APIs or React/Vue patterns",
        "reason": "Rarely needed in modern frameworks"
    },
    "axios": {
        "size": "14KB",
        "alternative": "Native fetch API (0KB) or ky (3KB)",
        "reason": "Fetch API covers most use cases"
    },
    "underscore": {
        "size": "17KB",
        "alternative": "Native ES6+ methods or lodash-es",
        "reason": "Most utilities now in standard JavaScript"
    },
    "chart.js": {
        "size": "180KB",
        "alternative": "recharts (bundled with React) or lightweight-charts",
        "reason": "Consider if you need all chart types"
    },
    "three": {
        "size": "600KB",
        "alternative": "None - use dynamic import for 3D features",
        "reason": "Very large, should be lazy-loaded"
    },
    "firebase": {
        "size": "400KB+",
        "alternative": "Import specific modules (firebase/auth, firebase/firestore)",
        "reason": "Modular imports significantly reduce size"
    },
    "material-ui": {
        "size": "Large",
        "alternative": "shadcn/ui (copy-paste components) or Tailwind",
        "reason": "Heavy runtime, consider headless alternatives"
    },
    "@mui/material": {
        "size": "Large",
        "alternative": "shadcn/ui or Radix UI + Tailwind",
        "reason": "Heavy runtime, consider headless alternatives"
    },
    "antd": {
        "size": "Large",
        "alternative": "shadcn/ui or Radix UI + Tailwind",
        "reason": "Heavy runtime, consider headless alternatives"
    }
}
PACKAGE_OPTIMIZATIONS = {
    "react-icons": "Import individual icons: import { FaHome } from 'react-icons/fa'",
    "date-fns": "Use tree-shaking: import { format } from 'date-fns'",
    "@heroicons/react": "Already tree-shakeable, good choice",
    "lucide-react": "Already tree-shakeable, add to optimizePackageImports in next.config.js",
    "framer-motion": "Use dynamic import for non-critical animations",
    "recharts": "Consider lazy loading for dashboard charts",
}
DEV_ONLY_PACKAGES = [
    "typescript", "@types/", "eslint", "prettier", "jest", "vitest",
    "@testing-library", "cypress", "playwright", "storybook", "@storybook",
    "webpack", "vite", "rollup", "esbuild", "tailwindcss", "postcss",
    "autoprefixer", "sass", "less", "husky", "lint-staged"
]
def load_package_json(project_dir: Path) -> Optional[Dict]:
    """Load and parse package.json."""
    package_path = project_dir / "package.json"
    if not package_path.exists():
        return None

    try:
        with open(package_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None
