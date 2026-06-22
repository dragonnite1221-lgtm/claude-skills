# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from values_validator_base import *  # noqa: F403,E402
# fmt: off
from values_validator_p1 import SNAKE_CASE_PATTERN, UPPER_CASE_PATTERN  # noqa: E402,E501
# fmt: on


def parse_values(content):
    """Parse values.yaml into structured data with metadata.

    Returns a list of entries with key paths, values, depth, and comment info.
    """
    entries = []
    key_stack = []
    indent_stack = [0]
    prev_comment = None

    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        # Track comments for documentation coverage
        if stripped.startswith("#"):
            prev_comment = stripped
            continue

        if not stripped:
            prev_comment = None
            continue

        indent = len(line) - len(line.lstrip())

        # Pop stack for dedented lines
        while len(indent_stack) > 1 and indent <= indent_stack[-1]:
            indent_stack.pop()
            if key_stack:
                key_stack.pop()

        # Parse key: value
        match = re.match(r"^(\S+)\s*:\s*(.*)", stripped)
        if match and not stripped.startswith("-"):
            key = match.group(1)
            raw_value = match.group(2).strip()

            # Check for inline comment
            inline_comment = None
            if "#" in raw_value:
                val_part, _, comment_part = raw_value.partition("#")
                raw_value = val_part.strip()
                inline_comment = comment_part.strip()

            # Build full key path
            full_path = ".".join(key_stack + [key])
            depth = len(key_stack) + 1

            # Determine value type
            value_type = "unknown"
            if not raw_value or raw_value == "":
                value_type = "map"
                key_stack.append(key)
                indent_stack.append(indent)
            elif raw_value in ("true", "false"):
                value_type = "boolean"
            elif raw_value == "null" or raw_value == "~":
                value_type = "null"
            elif raw_value == "{}":
                value_type = "empty_map"
            elif raw_value == "[]":
                value_type = "empty_list"
            elif re.match(r"^-?\d+$", raw_value):
                value_type = "integer"
            elif re.match(r"^-?\d+\.\d+$", raw_value):
                value_type = "float"
            elif raw_value.startswith('"') or raw_value.startswith("'"):
                value_type = "string"
            else:
                value_type = "string"

            has_doc = prev_comment is not None or inline_comment is not None

            entries.append({
                "key": key,
                "full_path": full_path,
                "value": raw_value,
                "value_type": value_type,
                "depth": depth,
                "line": line_num,
                "has_documentation": has_doc,
                "comment": prev_comment or inline_comment,
            })

            prev_comment = None
        else:
            prev_comment = None

    return entries
def to_camel_case(name):
    """Convert snake_case or kebab-case to camelCase."""
    parts = re.split(r"[-_]", name)
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])
def validate_naming(entries):
    """Check key naming conventions."""
    findings = []

    for entry in entries:
        key = entry["key"]

        # Skip map entries (they're parent keys)
        if entry["value_type"] == "map":
            # Parent keys should still be camelCase
            pass

        if SNAKE_CASE_PATTERN.match(key):
            findings.append({
                "severity": "medium",
                "category": "naming",
                "message": f"Key '{entry['full_path']}' uses snake_case — Helm convention is camelCase",
                "fix": f"Rename to camelCase: {to_camel_case(key)}",
                "line": entry["line"],
            })
        elif UPPER_CASE_PATTERN.match(key) and not key.isupper():
            findings.append({
                "severity": "medium",
                "category": "naming",
                "message": f"Key '{entry['full_path']}' starts with uppercase — use camelCase",
                "fix": f"Rename: {key[0].lower() + key[1:]}",
                "line": entry["line"],
            })
        elif "-" in key:
            findings.append({
                "severity": "medium",
                "category": "naming",
                "message": f"Key '{entry['full_path']}' uses kebab-case — Helm convention is camelCase",
                "fix": f"Rename to camelCase: {to_camel_case(key)}",
                "line": entry["line"],
            })

    return findings
