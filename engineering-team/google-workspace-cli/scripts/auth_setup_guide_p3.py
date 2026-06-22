# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from auth_setup_guide_base import *  # noqa: F403,E402
# fmt: off
from auth_setup_guide_p1 import OAUTH_GUIDE, SERVICE_ACCOUNT_GUIDE, SERVICE_SCOPES  # noqa: E402,E501
from auth_setup_guide_p2 import DEMO_VALIDATION, ENV_TEMPLATE, check_auth_status, validate_services  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Guided authentication setup for Google Workspace CLI (gws)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --guide oauth               # OAuth setup instructions
  %(prog)s --guide service-account      # Service account setup
  %(prog)s --scopes gmail,drive         # Show required scopes
  %(prog)s --generate-env               # Generate .env template
  %(prog)s --check                      # Check current auth status
  %(prog)s --validate --json            # Validate all services (JSON)
        """,
    )
    parser.add_argument("--guide", choices=["oauth", "service-account"],
                        help="Print setup guide")
    parser.add_argument("--scopes", help="Comma-separated services to show scopes for")
    parser.add_argument("--generate-env", action="store_true",
                        help="Generate .env template")
    parser.add_argument("--check", action="store_true",
                        help="Check current auth status")
    parser.add_argument("--validate", action="store_true",
                        help="Validate auth by testing services")
    parser.add_argument("--services", default="gmail,drive,calendar,sheets,tasks",
                        help="Services to validate (default: gmail,drive,calendar,sheets,tasks)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not any([args.guide, args.scopes, args.generate_env, args.check, args.validate]):
        parser.print_help()
        return

    if args.guide:
        if args.guide == "oauth":
            print(OAUTH_GUIDE)
        else:
            print(SERVICE_ACCOUNT_GUIDE)
        return

    if args.scopes:
        services = [s.strip() for s in args.scopes.split(",") if s.strip()]
        if args.json:
            output = {}
            for svc in services:
                output[svc] = SERVICE_SCOPES.get(svc, [])
            print(json.dumps(output, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  REQUIRED OAUTH SCOPES")
            print(f"{'='*60}\n")
            for svc in services:
                scopes = SERVICE_SCOPES.get(svc, [])
                print(f"  {svc.upper()}:")
                if scopes:
                    for scope in scopes:
                        print(f"    - {scope}")
                else:
                    print(f"    (no scopes defined for '{svc}')")
                print()
            # Print combined for easy copy-paste
            all_scopes = []
            for svc in services:
                all_scopes.extend(SERVICE_SCOPES.get(svc, []))
            if all_scopes:
                print(f"  COMBINED (for consent screen):")
                print(f"  {','.join(all_scopes)}")
            print(f"\n{'='*60}\n")
        return

    if args.generate_env:
        print(ENV_TEMPLATE)
        return

    if args.check:
        if shutil.which("gws"):
            status = check_auth_status()
        else:
            status = {"status": "gws_not_found",
                      "note": "Install gws first: cargo install gws-cli  OR  https://github.com/googleworkspace/cli/releases"}
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\nAuth Status: {status.get('status', 'unknown')}")
            for k, v in status.items():
                if k != "status":
                    print(f"  {k}: {v}")
            print()
        return

    if args.validate:
        services = [s.strip() for s in args.services.split(",") if s.strip()]
        if not shutil.which("gws"):
            report = DEMO_VALIDATION
        else:
            report = validate_services(services)

        if args.json:
            print(json.dumps(asdict(report), indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  AUTH VALIDATION REPORT")
            if report.demo_mode:
                print(f"  (DEMO MODE)")
            print(f"{'='*60}\n")
            if report.user:
                print(f"  User: {report.user}")
                print(f"  Method: {report.auth_method}\n")
            for r in report.results:
                icon = "PASS" if r["status"] == "PASS" else "FAIL"
                print(f"  [{icon}] {r['service']}: {r['message']}")
            print(f"\n  {report.summary}")
            print(f"\n{'='*60}\n")
