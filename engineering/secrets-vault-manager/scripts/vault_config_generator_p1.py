# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vault_config_generator_base import *  # noqa: F403,E402


AUTH_METHOD_DEFAULTS = {
    "approle": {
        "token_ttl": "1h",
        "token_max_ttl": "4h",
        "secret_id_num_uses": 1,
        "secret_id_ttl": "10m",
    },
    "kubernetes": {
        "token_ttl": "1h",
        "token_max_ttl": "4h",
    },
    "oidc": {
        "token_ttl": "8h",
        "token_max_ttl": "12h",
    },
}
SECRET_TYPE_MAP = {
    "db-creds": {
        "engine": "database",
        "path": "database/creds/{app}-readonly",
        "capabilities": ["read"],
        "description": "Dynamic database credentials",
    },
    "db-admin": {
        "engine": "database",
        "path": "database/creds/{app}-readwrite",
        "capabilities": ["read"],
        "description": "Dynamic database admin credentials",
    },
    "api-key": {
        "engine": "kv-v2",
        "path": "secret/data/{env}/{app}/api-keys",
        "capabilities": ["read"],
        "description": "Static API keys (KV v2)",
    },
    "tls-cert": {
        "engine": "pki",
        "path": "pki/issue/{app}-cert",
        "capabilities": ["create", "update"],
        "description": "TLS certificate issuance",
    },
    "encryption": {
        "engine": "transit",
        "path": "transit/encrypt/{app}-key",
        "capabilities": ["update"],
        "description": "Transit encryption operations",
    },
    "ssh-cert": {
        "engine": "ssh",
        "path": "ssh/sign/{app}-role",
        "capabilities": ["create", "update"],
        "description": "SSH certificate signing",
    },
    "config": {
        "engine": "kv-v2",
        "path": "secret/data/{env}/{app}/config",
        "capabilities": ["read"],
        "description": "Application configuration secrets",
    },
}
def parse_secrets(secrets_str):
    """Parse comma-separated secret types into list."""
    secrets = [s.strip() for s in secrets_str.split(",") if s.strip()]
    valid = []
    unknown = []
    for s in secrets:
        if s in SECRET_TYPE_MAP:
            valid.append(s)
        else:
            unknown.append(s)
    return valid, unknown
def generate_policy_hcl(app_name, secrets, environment="production"):
    """Generate HCL policy document."""
    lines = [
        f'# Vault policy for {app_name}',
        f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'# Environment: {environment}',
        '',
    ]

    for secret_type in secrets:
        tmpl = SECRET_TYPE_MAP[secret_type]
        path = tmpl["path"].format(app=app_name, env=environment)
        caps = ", ".join(f'"{c}"' for c in tmpl["capabilities"])

        lines.append(f'# {tmpl["description"]}')
        lines.append(f'path "{path}" {{')
        lines.append(f'  capabilities = [{caps}]')
        lines.append('}')
        lines.append('')

    # Always deny sys paths
    lines.append('# Deny admin paths')
    lines.append('path "sys/*" {')
    lines.append('  capabilities = ["deny"]')
    lines.append('}')

    return "\n".join(lines)
