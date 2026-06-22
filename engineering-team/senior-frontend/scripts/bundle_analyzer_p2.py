# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from bundle_analyzer_base import *  # noqa: F403,E402
# fmt: off
from bundle_analyzer_p1 import DEV_ONLY_PACKAGES, HEAVY_PACKAGES, PACKAGE_OPTIMIZATIONS  # noqa: E402,E501
# fmt: on


def analyze_dependencies(package_json: Dict) -> Dict:
    """Analyze dependencies for issues."""
    deps = package_json.get("dependencies", {})
    dev_deps = package_json.get("devDependencies", {})

    issues = []
    warnings = []
    optimizations = []

    # Check for heavy packages
    for pkg, info in HEAVY_PACKAGES.items():
        if pkg in deps:
            issues.append({
                "package": pkg,
                "type": "heavy_dependency",
                "size": info["size"],
                "alternative": info["alternative"],
                "reason": info["reason"]
            })

    # Check for dev dependencies in production
    for pkg in deps.keys():
        for dev_pattern in DEV_ONLY_PACKAGES:
            if dev_pattern in pkg:
                warnings.append({
                    "package": pkg,
                    "type": "dev_in_production",
                    "message": f"{pkg} should be in devDependencies, not dependencies"
                })

    # Check for optimization opportunities
    for pkg in deps.keys():
        for opt_pkg, opt_tip in PACKAGE_OPTIMIZATIONS.items():
            if opt_pkg in pkg:
                optimizations.append({
                    "package": pkg,
                    "tip": opt_tip
                })

    # Check for outdated React patterns
    if "prop-types" in deps and ("typescript" in dev_deps or "@types/react" in dev_deps):
        warnings.append({
            "package": "prop-types",
            "type": "redundant",
            "message": "prop-types is redundant when using TypeScript"
        })

    # Check for multiple state management libraries
    state_libs = ["redux", "@reduxjs/toolkit", "mobx", "zustand", "jotai", "recoil", "valtio"]
    found_state_libs = [lib for lib in state_libs if lib in deps]
    if len(found_state_libs) > 1:
        warnings.append({
            "packages": found_state_libs,
            "type": "multiple_state_libs",
            "message": f"Multiple state management libraries found: {', '.join(found_state_libs)}"
        })

    return {
        "total_dependencies": len(deps),
        "total_dev_dependencies": len(dev_deps),
        "issues": issues,
        "warnings": warnings,
        "optimizations": optimizations
    }
def check_nextjs_config(project_dir: Path) -> Dict:
    """Check Next.js configuration for optimizations."""
    config_paths = [
        project_dir / "next.config.js",
        project_dir / "next.config.mjs",
        project_dir / "next.config.ts"
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                content = config_path.read_text()
                suggestions = []

                # Check for image optimization
                if "images" not in content:
                    suggestions.append("Configure images.remotePatterns for optimized image loading")

                # Check for package optimization
                if "optimizePackageImports" not in content:
                    suggestions.append("Add experimental.optimizePackageImports for lucide-react, @heroicons/react")

                # Check for transpilePackages
                if "transpilePackages" not in content and "swc" not in content:
                    suggestions.append("Consider transpilePackages for monorepo packages")

                return {
                    "found": True,
                    "path": str(config_path),
                    "suggestions": suggestions
                }
            except Exception:
                pass

    return {
        "found": False,
        "suggestions": ["Create next.config.js with image and bundle optimizations"]
    }
