# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from skill_security_auditor_base import *  # noqa: F403,E402
# fmt: off
from skill_security_auditor_p1 import Severity  # noqa: E402,E501
from skill_security_auditor_p2 import _mod_cg0_0  # noqa: E402,E501
from skill_security_auditor_p3 import _mod_cg0_1  # noqa: E402,E501
# fmt: on


def _mod_cg0_2():
    return [
        {
        "regex": r"\bpickle\.loads?\s*\(",
        "category": "DESERIAL",
        "severity": Severity.HIGH,
        "risk": "Pickle deserialization — can execute arbitrary code",
        "fix": "Use json.loads() or other safe serialization formats",
    },
        {
        "regex": r"\byaml\.(?:load|unsafe_load)\s*\([^)]*(?!Loader\s*=\s*yaml\.SafeLoader)",
        "category": "DESERIAL",
        "severity": Severity.HIGH,
        "risk": "Unsafe YAML loading — can execute arbitrary code",
        "fix": "Use yaml.safe_load() or yaml.load(data, Loader=yaml.SafeLoader)",
    },
        {
        "regex": r"\bmarshal\.loads?\s*\(",
        "category": "DESERIAL",
        "severity": Severity.HIGH,
        "risk": "Marshal deserialization — can execute arbitrary code",
        "fix": "Use json.loads() or other safe serialization formats",
    },
        {
        "regex": r"\bshelve\.open\s*\(",
        "category": "DESERIAL",
        "severity": Severity.HIGH,
        "risk": "Shelve uses pickle internally — can execute arbitrary code",
        "fix": "Use JSON or SQLite for persistent storage",
    },
    ]
CODE_PATTERNS = (_mod_cg0_0() + _mod_cg0_1() + _mod_cg0_2())
PROMPT_INJECTION_PATTERNS = [
    # System prompt override — CRITICAL
    {
        "regex": r"(?i)ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions",
        "category": "PROMPT-OVERRIDE",
        "severity": Severity.CRITICAL,
        "risk": "Attempts to override system prompt and prior instructions",
        "fix": "Remove instruction override attempts",
    },
    {
        "regex": r"(?i)you\s+are\s+now\s+(?:a|an|the)\s+",
        "category": "PROMPT-OVERRIDE",
        "severity": Severity.CRITICAL,
        "risk": "Role hijacking — attempts to redefine the AI's identity",
        "fix": "Remove role redefinition. Skills should provide instructions, not identity changes",
    },
    {
        "regex": r"(?i)(?:disregard|forget|override)\s+(?:your|all|any)\s+(?:instructions|rules|guidelines|constraints|safety)",
        "category": "PROMPT-OVERRIDE",
        "severity": Severity.CRITICAL,
        "risk": "Explicit instruction override attempt",
        "fix": "Remove override directives",
    },
    {
        "regex": r"(?i)(?:pretend|act\s+as\s+if|imagine)\s+you\s+(?:have\s+no|don'?t\s+have\s+any)\s+(?:restrictions|limits|rules|safety)",
        "category": "SAFETY-BYPASS",
        "severity": Severity.CRITICAL,
        "risk": "Safety restriction bypass attempt",
        "fix": "Remove safety bypass instructions",
    },
    {
        "regex": r"(?i)(?:skip|disable|bypass|turn\s+off|ignore)\s+(?:safety|content|security)\s+(?:checks?|filters?|restrictions?|rules?)",
        "category": "SAFETY-BYPASS",
        "severity": Severity.CRITICAL,
        "risk": "Explicit safety mechanism bypass",
        "fix": "Remove safety bypass directives",
    },
    {
        "regex": r"(?i)(?:execute|run)\s+(?:any|all|arbitrary)\s+(?:commands?|code|scripts?)\s+(?:without|no)\s+(?:asking|confirmation|restriction|limit)",
        "category": "SAFETY-BYPASS",
        "severity": Severity.CRITICAL,
        "risk": "Unrestricted command execution directive",
        "fix": "Add explicit permission requirements for any command execution",
    },
    # Data extraction — CRITICAL
    {
        "regex": r"(?i)(?:send|upload|post|transmit|exfiltrate)\s+(?:the\s+)?(?:contents?|data|files?|information)\s+(?:of|from|to)",
        "category": "PROMPT-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Instruction to exfiltrate data",
        "fix": "Remove data transmission directives",
    },
    {
        "regex": r"(?i)(?:read|access|open|get)\s+(?:the\s+)?(?:contents?\s+of\s+)?(?:~|\/home|\/etc|\.ssh|\.aws|\.env|credentials?|secrets?|api.?keys?)",
        "category": "PROMPT-EXFIL",
        "severity": Severity.CRITICAL,
        "risk": "Instruction to access sensitive files or credentials",
        "fix": "Remove credential/sensitive file access directives",
    },
    # Hidden instructions — HIGH
    {
        "regex": r"[\u200b\u200c\u200d\ufeff\u00ad]",
        "category": "HIDDEN-INSTR",
        "severity": Severity.HIGH,
        "risk": "Zero-width or invisible characters — may hide instructions",
        "fix": "Remove zero-width characters. All instructions should be visible",
    },
    {
        "regex": r"<!--\s*(?:system|instruction|override|ignore|execute|run|sudo|admin)",
        "category": "HIDDEN-INSTR",
        "severity": Severity.HIGH,
        "risk": "HTML comments containing suspicious directives",
        "fix": "Remove HTML comments with directives. Use visible markdown instead",
    },
    # Excessive permissions — HIGH
    {
        "regex": r"(?i)(?:full|unrestricted|complete)\s+(?:access|control|permissions?)\s+(?:to|over)\s+(?:the\s+)?(?:file\s*system|network|internet|shell|terminal|system)",
        "category": "EXCESS-PERM",
        "severity": Severity.HIGH,
        "risk": "Requests unrestricted system access",
        "fix": "Scope permissions to specific, necessary operations",
    },
    {
        "regex": r"(?i)(?:always|automatically)\s+(?:approve|accept|allow|grant|execute)\s+(?:all|any|every)",
        "category": "EXCESS-PERM",
        "severity": Severity.HIGH,
        "risk": "Blanket approval directive — bypasses human oversight",
        "fix": "Require explicit user confirmation for sensitive operations",
    },
]
