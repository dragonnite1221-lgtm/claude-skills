# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from values_validator_base import *  # noqa: F403,E402


DEMO_VALUES = """# Default values for demo-app
replicaCount: 1

image:
  repository: nginx
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false

resources: {}

PASSWORD: supersecret123
db_password: changeme
api-key: sk-12345

deeply:
  nested:
    structure:
      that:
        goes:
          too:
            deep: true

undocumented_value: something
AnotherValue: 42
snake_case_key: bad
"""
NAMING_PATTERN = re.compile(r"^[a-z][a-zA-Z0-9]*$")  # camelCase
SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")  # snake_case
UPPER_CASE_PATTERN = re.compile(r"^[A-Z]")  # Starts with uppercase
SECRET_KEY_PATTERNS = [
    re.compile(r"(?:password|secret|token|apiKey|api_key|api-key|private_key|credentials)", re.IGNORECASE),
]
KNOWN_STRUCTURES = {
    "image": ["repository", "tag", "pullPolicy"],
    "service": ["type", "port"],
    "ingress": ["enabled"],
    "resources": [],
    "serviceAccount": ["create", "name"],
    "autoscaling": ["enabled", "minReplicas", "maxReplicas"],
}
