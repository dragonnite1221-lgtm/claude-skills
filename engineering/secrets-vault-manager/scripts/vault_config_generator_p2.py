# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vault_config_generator_base import *  # noqa: F403,E402
# fmt: off
from vault_config_generator_p1 import AUTH_METHOD_DEFAULTS, SECRET_TYPE_MAP, generate_policy_hcl, parse_secrets  # noqa: E402,E501
# fmt: on


def generate_auth_config(app_name, auth_method, policy_name, namespace=None):
    """Generate auth method setup commands."""
    commands = []
    defaults = AUTH_METHOD_DEFAULTS.get(auth_method, {})

    if auth_method == "approle":
        cmd = (
            f"vault write auth/approle/role/{app_name} \\\n"
            f"  token_ttl={defaults['token_ttl']} \\\n"
            f"  token_max_ttl={defaults['token_max_ttl']} \\\n"
            f"  secret_id_num_uses={defaults['secret_id_num_uses']} \\\n"
            f"  secret_id_ttl={defaults['secret_id_ttl']} \\\n"
            f"  token_policies=\"{policy_name}\""
        )
        commands.append({"description": f"Create AppRole for {app_name}", "command": cmd})

        commands.append({
            "description": "Fetch RoleID",
            "command": f"vault read auth/approle/role/{app_name}/role-id",
        })
        commands.append({
            "description": "Generate SecretID (single-use)",
            "command": f"vault write -f auth/approle/role/{app_name}/secret-id",
        })

    elif auth_method == "kubernetes":
        ns = namespace or "default"
        cmd = (
            f"vault write auth/kubernetes/role/{app_name} \\\n"
            f"  bound_service_account_names={app_name} \\\n"
            f"  bound_service_account_namespaces={ns} \\\n"
            f"  policies={policy_name} \\\n"
            f"  ttl={defaults['token_ttl']}"
        )
        commands.append({"description": f"Create Kubernetes auth role for {app_name}", "command": cmd})

    elif auth_method == "oidc":
        cmd = (
            f"vault write auth/oidc/role/{app_name} \\\n"
            f"  bound_audiences=\"vault\" \\\n"
            f"  allowed_redirect_uris=\"https://vault.example.com/ui/vault/auth/oidc/oidc/callback\" \\\n"
            f"  user_claim=\"email\" \\\n"
            f"  oidc_scopes=\"openid,profile,email\" \\\n"
            f"  policies=\"{policy_name}\" \\\n"
            f"  ttl={defaults['token_ttl']}"
        )
        commands.append({"description": f"Create OIDC role for {app_name}", "command": cmd})

    return commands
def build_output(app_name, auth_method, secrets, environment, namespace):
    """Build complete configuration output."""
    valid_secrets, unknown_secrets = parse_secrets(secrets)

    if not valid_secrets:
        return {
            "error": "No valid secret types provided",
            "unknown": unknown_secrets,
            "available_types": list(SECRET_TYPE_MAP.keys()),
        }

    policy_name = f"{app_name}-policy"
    policy_hcl = generate_policy_hcl(app_name, valid_secrets, environment)
    auth_commands = generate_auth_config(app_name, auth_method, policy_name, namespace)

    secret_details = []
    for s in valid_secrets:
        tmpl = SECRET_TYPE_MAP[s]
        secret_details.append({
            "type": s,
            "engine": tmpl["engine"],
            "path": tmpl["path"].format(app=app_name, env=environment),
            "capabilities": tmpl["capabilities"],
            "description": tmpl["description"],
        })

    result = {
        "app_name": app_name,
        "auth_method": auth_method,
        "environment": environment,
        "policy_name": policy_name,
        "policy_hcl": policy_hcl,
        "auth_commands": auth_commands,
        "secrets": secret_details,
        "generated_at": datetime.now().isoformat(),
    }

    if unknown_secrets:
        result["warnings"] = [f"Unknown secret type '{u}' — skipped. Available: {list(SECRET_TYPE_MAP.keys())}" for u in unknown_secrets]
    if namespace:
        result["namespace"] = namespace

    return result
def print_human(result):
    """Print human-readable output."""
    if "error" in result:
        print(f"ERROR: {result['error']}")
        if result.get("unknown"):
            print(f"  Unknown types: {', '.join(result['unknown'])}")
        print(f"  Available types: {', '.join(result['available_types'])}")
        sys.exit(1)

    print(f"=== Vault Configuration for {result['app_name']} ===")
    print(f"Auth Method: {result['auth_method']}")
    print(f"Environment: {result['environment']}")
    print(f"Policy Name: {result['policy_name']}")
    print()

    if result.get("warnings"):
        for w in result["warnings"]:
            print(f"WARNING: {w}")
        print()

    print("--- Policy HCL ---")
    print(result["policy_hcl"])
    print()

    print(f"Write policy: vault policy write {result['policy_name']} {result['policy_name']}.hcl")
    print()

    print("--- Auth Method Setup ---")
    for cmd_info in result["auth_commands"]:
        print(f"# {cmd_info['description']}")
        print(cmd_info["command"])
        print()

    print("--- Secret Paths ---")
    for s in result["secrets"]:
        caps = ", ".join(s["capabilities"])
        print(f"  {s['type']:15s}  {s['path']:50s}  [{caps}]")
