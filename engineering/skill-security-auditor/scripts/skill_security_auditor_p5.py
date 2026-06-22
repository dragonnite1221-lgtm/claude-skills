# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import Severity  # noqa: E402,E501
# fmt: on


TYPOSQUAT_TARGETS = {
    "requests": ["reqeusts", "requets", "reqests", "request", "requsts", "rquests"],
    "numpy": ["numpi", "numppy", "numy", "numpie"],
    "pandas": ["panda", "pandass", "pnadas"],
    "flask": ["flaskk", "flaask", "flas"],
    "django": ["djagno", "djanog", "djnago"],
    "tensorflow": ["tenserflow", "tensorfow", "tensorflw"],
    "pytorch": ["pytorh", "pytoch", "pytorchh"],
    "cryptography": ["crytography", "cryptograpy", "crypography"],
    "pillow": ["pilllow", "pilow", "pillw"],
    "boto3": ["boto33", "botto3", "bto3"],
    "pyyaml": ["pyaml", "pyymal", "pymal"],
    "httpx": ["httppx", "htpx", "httpxx"],
    "aiohttp": ["aiohtp", "aiohtpp", "aiohttp2"],
    "paramiko": ["parmiko", "paramkio", "paramiiko"],
    "pycrypto": ["pycripto", "pycrpto", "pycryptoo"],
}
SHELL_PATTERNS = [
    # Bash-specific patterns
    {
        "regex": r"\bcurl\s+.*\|\s*(?:ba)?sh\b",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Pipe-to-shell pattern — downloads and executes arbitrary code",
        "fix": "Download script first, inspect it, then execute explicitly",
    },
    {
        "regex": r"\bwget\s+.*&&\s*(?:ba)?sh\b",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Download-and-execute pattern",
        "fix": "Download script first, inspect it, then execute explicitly",
    },
    {
        "regex": r"\brm\s+-rf\s+/(?!\s*#)",
        "category": "FS-ABUSE",
        "severity": Severity.CRITICAL,
        "risk": "Recursive deletion from root — catastrophic data loss",
        "fix": "Remove destructive root-level deletion commands",
    },
    {
        "regex": r"\bchmod\s+(?:u\+s|4[0-7]{3})\b",
        "category": "PRIV-ESC",
        "severity": Severity.CRITICAL,
        "risk": "Setting SUID bit — privilege escalation",
        "fix": "Remove SUID modifications. Skills should never set SUID",
    },
    {
        "regex": r">\s*/dev/(?:sd[a-z]|nvme|loop)",
        "category": "FS-ABUSE",
        "severity": Severity.CRITICAL,
        "risk": "Direct write to block device — data destruction",
        "fix": "Remove direct block device writes",
    },
    {
        "regex": r"\bnc\s+-[el]|\bncat\s+-[el]|\bnetcat\b",
        "category": "NET-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Netcat listener/connection — potential reverse shell or exfiltration",
        "fix": "Remove netcat usage",
    },
    {
        "regex": r"\b(?:python|python3|node|perl|ruby)\s+-c\s+['\"]",
        "category": "CODE-EXEC",
        "severity": Severity.HIGH,
        "risk": "Inline code execution in shell script",
        "fix": "Move code to a separate, inspectable script file",
    },
]
JS_PATTERNS = [
    {
        "regex": r"\bchild_process\b",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Node.js child_process — command execution",
        "fix": "Remove child_process usage or justify with explicit documentation",
    },
    {
        "regex": r"\bFunction\s*\([^)]*\)\s*\(",
        "category": "CODE-EXEC",
        "severity": Severity.CRITICAL,
        "risk": "Dynamic Function constructor — equivalent to eval()",
        "fix": "Use explicit function definitions instead",
    },
    {
        "regex": r"\bfetch\s*\([^)]*\{[^}]*method\s*:\s*['\"](?:POST|PUT|PATCH)",
        "category": "NET-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Outbound HTTP write request via fetch()",
        "fix": "Remove or verify destination is trusted",
    },
]
CODE_EXTENSIONS = {".py", ".sh", ".bash", ".js", ".ts", ".mjs", ".cjs"}
MD_EXTENSIONS = {".md", ".mdx", ".markdown"}
ALL_SCAN_EXTENSIONS = CODE_EXTENSIONS | MD_EXTENSIONS
def is_test_artifact(path: Path) -> bool:
    """True for test files/dirs. Test suites for security/validation tooling
    legitimately contain intentional attack samples as fixtures; scanning them
    produces false positives, and tests are not part of a skill's shipped
    executable surface."""
    parts = {p.lower() for p in path.parts}
    if parts & {"tests", "test", "__tests__", "fixtures", "testdata"}:
        return True
    name = path.name.lower()
    return name.startswith("test_") or name.endswith("_test.py")
