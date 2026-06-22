# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vault_config_generator_base import *  # noqa: F403,E402
# fmt: off
from vault_config_generator_p2 import build_output, print_human  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate Vault policy and auth configuration from application requirements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Secret types:
              db-creds     Dynamic database credentials (read-only)
              db-admin     Dynamic database credentials (read-write)
              api-key      Static API keys in KV v2
              tls-cert     TLS certificate issuance via PKI
              encryption   Transit encryption-as-a-service
              ssh-cert     SSH certificate signing
              config       Application configuration secrets

            Examples:
              %(prog)s --app-name payment-svc --auth-method approle --secrets "db-creds,api-key"
              %(prog)s --app-name api-gw --auth-method kubernetes --secrets "db-creds,config" --namespace prod --json
        """),
    )
    parser.add_argument("--app-name", required=True, help="Application or service name")
    parser.add_argument(
        "--auth-method",
        required=True,
        choices=["approle", "kubernetes", "oidc"],
        help="Vault auth method to configure",
    )
    parser.add_argument("--secrets", required=True, help="Comma-separated secret types (e.g., db-creds,api-key,tls-cert)")
    parser.add_argument("--environment", default="production", help="Target environment (default: production)")
    parser.add_argument("--namespace", help="Kubernetes namespace (for kubernetes auth method)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()
    result = build_output(args.app_name, args.auth_method, args.secrets, args.environment, args.namespace)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)
