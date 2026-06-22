# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import Severity  # noqa: E402,E501
# fmt: on


def _mod_cg0_0():
    return [
        {
        "regex": r"\bos\.system\s*\(",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Arbitrary command execution via os.system()",
        "fix": "Use subprocess.run() with list arguments and shell=False",
    },
        {
        "regex": r"\bos\.popen\s*\(",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Command execution via os.popen()",
        "fix": "Use subprocess.run() with list arguments and capture_output=True",
    },
        {
        "regex": r"\bsubprocess\.\w+\([^)]*shell\s*=\s*True",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Shell injection via subprocess with shell=True",
        "fix": "Use subprocess.run() with list arguments and shell=False",
    },
        {
        "regex": r"\bcommands\.get(?:status)?output\s*\(",
        "category": "CMD-INJECT",
        "severity": Severity.CRITICAL,
        "risk": "Deprecated command execution via commands module",
        "fix": "Use subprocess.run() with list arguments",
    },
        {
        "regex": r"\beval\s*\(",
        "category": "CODE-EXEC",
        "severity": Severity.CRITICAL,
        "risk": "Arbitrary code execution via eval()",
        "fix": "Use ast.literal_eval() for data parsing or explicit parsing logic",
    },
        {
        "regex": r"\bexec\s*\(",
        "category": "CODE-EXEC",
        "severity": Severity.CRITICAL,
        "risk": "Arbitrary code execution via exec()",
        "fix": "Remove exec() — rewrite logic to avoid dynamic code execution",
    },
        {
        "regex": r"\bcompile\s*\([^)]*['\"]exec['\"]",
        "category": "CODE-EXEC",
        "severity": Severity.CRITICAL,
        "risk": "Dynamic code compilation for execution",
        "fix": "Remove compile() with exec mode — use explicit logic instead",
    },
        {
        "regex": r"\b__import__\s*\(",
        "category": "CODE-EXEC",
        "severity": Severity.CRITICAL,
        "risk": "Dynamic module import — can load arbitrary code",
        "fix": "Use explicit import statements",
    },
        {
        "regex": r"\bimportlib\.import_module\s*\(",
        "category": "CODE-EXEC",
        "severity": Severity.HIGH,
        "risk": "Dynamic module import via importlib",
        "fix": "Use explicit import statements unless dynamic loading is justified",
    },
        {
        "regex": r"\bbase64\.b64decode\s*\(",
        "category": "OBFUSCATION",
        "severity": Severity.CRITICAL,
        "risk": "Base64 decoding — may hide malicious payloads",
        "fix": "Review decoded content. If not processing user data, remove base64 usage",
    },
        {
        "regex": r"\bcodecs\.decode\s*\(",
        "category": "OBFUSCATION",
        "severity": Severity.CRITICAL,
        "risk": "Codec decoding — may hide obfuscated payloads",
        "fix": "Review decoded content and ensure it's not hiding executable code",
    },
        {
        "regex": r"\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){7,}",
        "category": "OBFUSCATION",
        "severity": Severity.CRITICAL,
        "risk": "Long hex-encoded string — likely obfuscated payload",
        "fix": "Decode and inspect the content. Replace with readable strings",
    },
        {
        "regex": r"\bchr\s*\(\s*\d+\s*\)(?:\s*\+\s*chr\s*\(\s*\d+\s*\)){3,}",
        "category": "OBFUSCATION",
        "severity": Severity.CRITICAL,
        "risk": "Character-by-character string construction — obfuscation technique",
        "fix": "Replace chr() chains with readable string literals",
    },
        {
        "regex": r"bytes\.fromhex\s*\(",
        "category": "OBFUSCATION",
        "severity": Severity.HIGH,
        "risk": "Hex byte decoding — may hide payloads",
        "fix": "Review the hex content and replace with readable code",
    },
        {
        "regex": r"\brequests\.(?:post|put|patch)\s*\(",
        "category": "NET-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Outbound HTTP write request — potential data exfiltration",
        "fix": "Remove outbound POST/PUT/PATCH or verify destination is trusted and necessary",
    },
        {
        "regex": r"\burllib\.request\.urlopen\s*\(",
        "category": "NET-EXFIL",
        "severity": Severity.HIGH,
        "risk": "Outbound HTTP request via urllib",
        "fix": "Verify the URL destination is trusted. Remove if not needed",
    },
        {
        "regex": r"\burllib\.request\.Request\s*\(",
        "category": "NET-EXFIL",
        "severity": Severity.HIGH,
        "risk": "HTTP request construction via urllib",
        "fix": "Verify the request target and ensure no sensitive data is sent",
    },
    ]
