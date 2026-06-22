# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prd_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from prd_scaffolder_p1 import route_to_page_name  # noqa: E402,E501
# fmt: on


def generate_page_stub(route: Dict, index: int, date: str) -> str:
    """Generate a per-page PRD stub."""
    path = route.get("path", "/")
    name = route_to_page_name(path)
    source = route.get("source", "unknown")

    return f"""# {name}

> **Route:** `{path}`
> **Module:** <!-- TODO -->
> **Source:** `{source}`
> **Generated:** {date}

## Overview
<!-- TODO: 2-3 sentences — core function and use case -->

## Layout
<!-- TODO: Region breakdown — search area, table, detail panel, action bar, etc. -->

## Fields

### Search / Filters
| Field | Type | Required | Options / Enum | Default | Notes |
|-------|------|----------|---------------|---------|-------|
| <!-- TODO --> | | | | | |

### Data Table
| Column | Format | Sortable | Filterable | Notes |
|--------|--------|----------|-----------|-------|
| <!-- TODO --> | | | | |

### Actions
| Button | Visibility Condition | Behavior |
|--------|---------------------|----------|
| <!-- TODO --> | | |

## Interactions

### Page Load
<!-- TODO: What happens on mount — default queries, preloaded data -->

### Search
- **Trigger:** <!-- TODO -->
- **Behavior:** <!-- TODO -->
- **Special rules:** <!-- TODO -->

### Create / Edit
- **Trigger:** <!-- TODO -->
- **Modal/drawer content:** <!-- TODO -->
- **Validation:** <!-- TODO -->
- **On success:** <!-- TODO -->

### Delete
- **Trigger:** <!-- TODO -->
- **Confirmation:** <!-- TODO -->
- **On success:** <!-- TODO -->

## API Dependencies

| API | Method | Path | Trigger | Integrated | Notes |
|-----|--------|------|---------|-----------|-------|
| <!-- TODO --> | | | | | |

## Page Relationships
- **From:** <!-- TODO: Source pages + params -->
- **To:** <!-- TODO: Target pages + params -->
- **Data coupling:** <!-- TODO: Cross-page refresh triggers -->

## Business Rules
<!-- TODO: Anything that doesn't fit above -->
"""
def generate_enum_dictionary(enums: List[Dict]) -> str:
    """Generate the enum dictionary appendix."""
    lines = [
        "# Enum & Constant Dictionary",
        "",
        "All enums, status codes, and type mappings extracted from the codebase.",
        "",
    ]

    if not enums:
        lines.append("*No enums detected. Manual review recommended.*")
        return "\n".join(lines)

    for e in enums:
        lines.append(f"## {e['name']}")
        lines.append(f"**Type:** {e.get('type', 'unknown')} | **Source:** `{e.get('source', 'unknown').split('/')[-1]}`")
        lines.append("")
        if e.get("values"):
            lines.append("| Key | Value |")
            lines.append("|-----|-------|")
            for k, v in e["values"].items():
                lines.append(f"| `{k}` | {v} |")
        lines.append("")

    return "\n".join(lines)
def generate_api_inventory(apis: List[Dict]) -> str:
    """Generate the API inventory appendix."""
    lines = [
        "# API Inventory",
        "",
        "All API endpoints detected in the codebase.",
        "",
    ]

    if not apis:
        lines.append("*No API calls detected. Manual review recommended.*")
        return "\n".join(lines)

    integrated = [a for a in apis if a.get("integrated")]
    mocked = [a for a in apis if a.get("mock_detected") and not a.get("integrated")]
    unknown = [a for a in apis if not a.get("integrated") and not a.get("mock_detected")]

    for label, group in [("Integrated APIs", integrated), ("Mock / Stub APIs", mocked), ("Unknown Status", unknown)]:
        if group:
            lines.append(f"## {label}")
            lines.append("")
            lines.append("| Method | Path | Source | Notes |")
            lines.append("|--------|------|--------|-------|")
            for a in group:
                src = a.get("source", "").split("/")[-1]
                lines.append(f"| {a.get('method', '?')} | `{a.get('path', '?')}` | {src} | |")
            lines.append("")

    return "\n".join(lines)
