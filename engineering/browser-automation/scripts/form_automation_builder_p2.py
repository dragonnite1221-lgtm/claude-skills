# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from form_automation_builder_base import *  # noqa: F403,E402
# fmt: off
from form_automation_builder_p1 import generate_field_action, validate_fields  # noqa: E402,E501
# fmt: on


def build_form_script(url, fields, output_format="script"):
    """Build a Playwright form automation script from the field specification."""

    issues = validate_fields(fields)
    if issues:
        return None, issues

    if output_format == "json":
        config = {
            "url": url,
            "fields": fields,
            "field_count": len(fields),
            "field_types": list(set(f["type"] for f in fields)),
            "has_file_upload": any(f["type"] == "file" for f in fields),
            "generated_at": datetime.now().isoformat(),
        }
        return config, None

    # Group fields into steps if step markers are present
    steps = {}
    for field in fields:
        step = field.get("step", 1)
        if step not in steps:
            steps[step] = []
        steps[step].append(field)

    multi_step = len(steps) > 1

    # Generate step functions
    step_functions = []
    for step_num in sorted(steps.keys()):
        step_fields = steps[step_num]
        actions = "\n".join(generate_field_action(f) for f in step_fields)

        if multi_step:
            fn = textwrap.dedent(f"""\
async def fill_step_{step_num}(page):
    \"\"\"Fill form step {step_num} ({len(step_fields)} fields).\"\"\"
    print(f"Filling step {step_num}...")
{actions}
    print(f"Step {step_num} complete.")
""")
        else:
            fn = textwrap.dedent(f"""\
async def fill_form(page):
    \"\"\"Fill form ({len(step_fields)} fields).\"\"\"
    print("Filling form...")
{actions}
    print("Form filled.")
""")
        step_functions.append(fn)

    step_functions_str = "\n\n".join(step_functions)

    # Generate main() call sequence
    if multi_step:
        step_calls = "\n".join(
            f"        await fill_step_{n}(page)" for n in sorted(steps.keys())
        )
    else:
        step_calls = "        await fill_form(page)"

    submit_selector = None
    for field in fields:
        if field.get("type") == "click" and field.get("is_submit"):
            submit_selector = field["selector"]
            break

    submit_block = ""
    if submit_selector:
        submit_block = textwrap.dedent(f"""\

        # Submit
        await page.click("{submit_selector}")
        await page.wait_for_load_state("networkidle")
        print("Form submitted.")
""")

    script = textwrap.dedent(f'''\
#!/usr/bin/env python3
"""
Auto-generated Playwright form automation script.
Target: {url}
Fields: {len(fields)}
Steps: {len(steps)}
Generated: {datetime.now().isoformat()}

Requirements:
    pip install playwright
    playwright install chromium
"""

import asyncio
import random
from playwright.async_api import async_playwright

URL = "{url}"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


{step_functions_str}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={{"width": 1920, "height": 1080}},
            user_agent=random.choice(USER_AGENTS),
        )
        page = await context.new_page()

        await page.add_init_script(
            "Object.defineProperty(navigator, \'webdriver\', {{get: () => undefined}});"
        )

        print(f"Navigating to {{URL}}...")
        await page.goto(URL, wait_until="networkidle")

{step_calls}
{submit_block}
        print("Automation complete.")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
''')

    return script, None
