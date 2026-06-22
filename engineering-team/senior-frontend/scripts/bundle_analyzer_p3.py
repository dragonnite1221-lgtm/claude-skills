# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from bundle_analyzer_base import *  # noqa: F403,E402


def analyze_imports(project_dir: Path) -> Dict:
    """Analyze import patterns in source files."""
    issues = []
    src_dirs = [project_dir / "src", project_dir / "app", project_dir / "pages"]

    patterns_to_check = [
        (r"import\s+\*\s+as\s+\w+\s+from\s+['\"]lodash['\"]", "Avoid import * from lodash, use individual imports"),
        (r"import\s+moment\s+from\s+['\"]moment['\"]", "Consider replacing moment with date-fns or dayjs"),
        (r"import\s+\{\s*\w+(?:,\s*\w+){5,}\s*\}\s+from\s+['\"]react-icons", "Import icons from specific icon sets (react-icons/fa)"),
    ]

    files_checked = 0
    for src_dir in src_dirs:
        if not src_dir.exists():
            continue

        for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            for file_path in src_dir.glob(f"**/{ext}"):
                if "node_modules" in str(file_path):
                    continue

                files_checked += 1
                try:
                    content = file_path.read_text()
                    for pattern, message in patterns_to_check:
                        if re.search(pattern, content):
                            issues.append({
                                "file": str(file_path.relative_to(project_dir)),
                                "issue": message
                            })
                except Exception:
                    continue

    return {
        "files_checked": files_checked,
        "issues": issues
    }
def calculate_score(analysis: Dict) -> Tuple[int, str]:
    """Calculate bundle health score."""
    score = 100

    # Deduct for heavy dependencies
    score -= len(analysis["dependencies"]["issues"]) * 10

    # Deduct for dev deps in production
    score -= len([w for w in analysis["dependencies"]["warnings"]
                  if w.get("type") == "dev_in_production"]) * 5

    # Deduct for import issues
    score -= len(analysis.get("imports", {}).get("issues", [])) * 3

    # Deduct for missing Next.js optimizations
    if not analysis.get("nextjs", {}).get("found", True):
        score -= 10

    score = max(0, min(100, score))

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    return score, grade
def print_report(analysis: Dict) -> None:
    """Print human-readable report."""
    score, grade = calculate_score(analysis)

    print("=" * 60)
    print("FRONTEND BUNDLE ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nBundle Health Score: {score}/100 ({grade})")

    deps = analysis["dependencies"]
    print(f"\nDependencies: {deps['total_dependencies']} production, {deps['total_dev_dependencies']} dev")

    # Heavy dependencies
    if deps["issues"]:
        print("\n--- HEAVY DEPENDENCIES ---")
        for issue in deps["issues"]:
            print(f"\n  {issue['package']} ({issue['size']})")
            print(f"    Reason: {issue['reason']}")
            print(f"    Alternative: {issue['alternative']}")

    # Warnings
    if deps["warnings"]:
        print("\n--- WARNINGS ---")
        for warning in deps["warnings"]:
            if "package" in warning:
                print(f"  - {warning['package']}: {warning['message']}")
            else:
                print(f"  - {warning['message']}")

    # Optimizations
    if deps["optimizations"]:
        print("\n--- OPTIMIZATION TIPS ---")
        for opt in deps["optimizations"]:
            print(f"  - {opt['package']}: {opt['tip']}")

    # Next.js config
    if "nextjs" in analysis:
        nextjs = analysis["nextjs"]
        if nextjs.get("suggestions"):
            print("\n--- NEXT.JS CONFIG ---")
            for suggestion in nextjs["suggestions"]:
                print(f"  - {suggestion}")

    # Import issues
    if analysis.get("imports", {}).get("issues"):
        print("\n--- IMPORT ISSUES ---")
        for issue in analysis["imports"]["issues"][:10]:  # Limit to 10
            print(f"  - {issue['file']}: {issue['issue']}")

    # Summary
    print("\n--- RECOMMENDATIONS ---")
    if score >= 90:
        print("  Bundle is well-optimized!")
    elif deps["issues"]:
        print("  1. Replace heavy dependencies with lighter alternatives")
    if deps["warnings"]:
        print("  2. Move dev-only packages to devDependencies")
    if deps["optimizations"]:
        print("  3. Apply import optimizations for tree-shaking")

    print("\n" + "=" * 60)
