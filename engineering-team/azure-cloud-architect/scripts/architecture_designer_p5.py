# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_designer_base import *  # noqa: F403,E402
# fmt: off
from architecture_designer_p3 import recommend  # noqa: E402,E501
from architecture_designer_p4 import _format_text, generate_checklist  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Azure Architecture Designer — recommend Azure architecture patterns based on application requirements.",
        epilog="Examples:\n"
               "  python architecture_designer.py --app-type web_app --users 10000\n"
               "  python architecture_designer.py --app-type microservices --users 50000 --json\n"
               '  python architecture_designer.py --app-type serverless --users 5000 --requirements \'{"compliance":["HIPAA"]}\'',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--app-type",
        required=True,
        choices=["web_app", "saas_platform", "mobile_backend", "microservices", "data_pipeline", "serverless"],
        help="Application type to design for",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=1000,
        help="Expected number of users (default: 1000)",
    )
    parser.add_argument(
        "--requirements",
        type=str,
        default="{}",
        help="JSON string of additional requirements (budget_monthly_usd, compliance, etc.)",
    )
    parser.add_argument(
        "--checklist",
        action="store_true",
        help="Include implementation checklist in output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of human-readable text",
    )

    args = parser.parse_args()

    try:
        reqs = json.loads(args.requirements)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid --requirements JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    result = recommend(args.app_type, args.users, reqs)

    if args.checklist:
        result["implementation_checklist"] = generate_checklist(result)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(_format_text(result))
        if args.checklist:
            print("\n--- Implementation Checklist ---")
            for phase in result["implementation_checklist"]:
                print(f"\n{phase['phase']}:")
                for task in phase["tasks"]:
                    print(f"  [ ] {task}")
