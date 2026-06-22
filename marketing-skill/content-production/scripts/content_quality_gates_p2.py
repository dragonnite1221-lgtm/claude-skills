# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_quality_gates_base import *  # noqa: F403,E402
# fmt: off
from content_quality_gates_p1 import DATE_RE, DEMO_CONTENT, FRONTMATTER_DATE_RE, check_heading_hierarchy, check_image_alt_text, check_meta_description, check_paragraph_length, check_self_promotion, check_source_citations, check_title_length  # noqa: E402,E501
# fmt: on


def check_freshness(text):
    """Gate 8: dateModified or update marker present."""
    findings = []
    has_date = bool(FRONTMATTER_DATE_RE.search(text)) or bool(DATE_RE.search(text))
    if not has_date:
        findings.append("No dateModified or 'Updated' marker. Evergreen content needs freshness signals.")
    return {"gate": "freshness-signal", "passed": len(findings) == 0, "findings": findings}
ALL_GATES = [
    check_heading_hierarchy,
    check_paragraph_length,
    check_image_alt_text,
    check_source_citations,
    check_title_length,
    check_meta_description,
    check_self_promotion,
    check_freshness,
]
def run_gates(text):
    results = [gate(text) for gate in ALL_GATES]
    passed = sum(1 for r in results if r["passed"])
    failed = [r for r in results if not r["passed"]]
    total = len(results)

    if len(failed) == 0:
        verdict = "PUBLISH"
    elif all(len(r["findings"]) <= 1 for r in failed) and len(failed) <= 2:
        verdict = "TARGET"
    else:
        verdict = "BLOCK"

    return {
        "status": "ok",
        "gates_passed": passed,
        "gates_total": total,
        "verdict": verdict,
        "results": results,
    }
def main():
    p = argparse.ArgumentParser(
        description="Non-negotiable quality gates for content publishing.",
        epilog="All gates must pass before publishing. Run with --demo for a sample article.",
    )
    p.add_argument("file", nargs="?", help="Markdown file to check")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--demo", action="store_true", help="Run with demo content")
    args = p.parse_args()

    if args.demo:
        text = DEMO_CONTENT
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"[error] {path} not found", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8", errors="replace")
    else:
        p.print_help()
        sys.exit(0)

    result = run_gates(text)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(f"Content Quality Gates — {result['gates_passed']}/{result['gates_total']} passed")
    print(f"Verdict: {result['verdict']}")
    print()
    for r in result["results"]:
        icon = "✅" if r["passed"] else "❌"
        print(f"  {icon} {r['gate']}")
        for f in r["findings"]:
            print(f"     → {f}")
    print()
    if result["verdict"] == "PUBLISH":
        print("  All gates pass. Ready to publish.")
    elif result["verdict"] == "TARGET":
        print("  Minor issues. Fix the flagged items, then publish.")
    else:
        print("  BLOCKED. Fix all gate failures before publishing.")
