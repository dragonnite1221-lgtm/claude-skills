# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from form_automation_builder_base import *  # noqa: F403,E402


SUPPORTED_FIELD_TYPES = {
    "text": "page.fill('{selector}', '{value}')",
    "password": "page.fill('{selector}', '{value}')",
    "email": "page.fill('{selector}', '{value}')",
    "textarea": "page.fill('{selector}', '{value}')",
    "select": "page.select_option('{selector}', value='{value}')",
    "checkbox": "page.check('{selector}')" if True else "page.uncheck('{selector}')",
    "radio": "page.check('{selector}')",
    "file": "page.set_input_files('{selector}', '{value}')",
    "click": "page.click('{selector}')",
}
def validate_fields(fields):
    """Validate the field specification format. Returns list of issues."""
    issues = []
    if not isinstance(fields, list):
        issues.append("Top-level structure must be a JSON array of field objects.")
        return issues

    for i, field in enumerate(fields):
        if not isinstance(field, dict):
            issues.append(f"Field {i}: must be a JSON object.")
            continue
        if "selector" not in field:
            issues.append(f"Field {i}: missing required 'selector' key.")
        if "type" not in field:
            issues.append(f"Field {i}: missing required 'type' key.")
        elif field["type"] not in SUPPORTED_FIELD_TYPES:
            issues.append(
                f"Field {i}: unsupported type '{field['type']}'. "
                f"Supported: {', '.join(sorted(SUPPORTED_FIELD_TYPES.keys()))}"
            )
        if field.get("type") not in ("checkbox", "radio", "click") and "value" not in field:
            issues.append(f"Field {i}: missing 'value' for type '{field.get('type', '?')}'.")

    return issues
def generate_field_action(field, indent=8):
    """Generate the Playwright action line for a single field."""
    ftype = field["type"]
    selector = field["selector"]
    value = field.get("value", "")
    label = field.get("label", selector)
    prefix = " " * indent

    lines = []
    lines.append(f'{prefix}# {label}')

    if ftype == "checkbox":
        if field.get("value", "true").lower() in ("true", "yes", "1", "on"):
            lines.append(f'{prefix}await page.check("{selector}")')
        else:
            lines.append(f'{prefix}await page.uncheck("{selector}")')
    elif ftype == "radio":
        lines.append(f'{prefix}await page.check("{selector}")')
    elif ftype == "click":
        lines.append(f'{prefix}await page.click("{selector}")')
    elif ftype == "select":
        lines.append(f'{prefix}await page.select_option("{selector}", value="{value}")')
    elif ftype == "file":
        lines.append(f'{prefix}await page.set_input_files("{selector}", "{value}")')
    else:
        # text, password, email, textarea
        lines.append(f'{prefix}await page.fill("{selector}", "{value}")')

    # Add optional wait_after
    wait_after = field.get("wait_after")
    if wait_after:
        lines.append(f'{prefix}await page.wait_for_selector("{wait_after}")')

    return "\n".join(lines)
