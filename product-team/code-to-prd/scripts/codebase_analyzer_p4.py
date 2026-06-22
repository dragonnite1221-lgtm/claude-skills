# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from codebase_analyzer_base import *  # noqa: F403,E402
# fmt: off
from codebase_analyzer_p1 import COMPONENT_EXTENSIONS, NEST_MODEL_PATTERNS, PYTHON_MODEL_PATTERNS  # noqa: E402,E501
# fmt: on


def extract_models(filepath: Path, framework: str) -> List[Dict[str, Any]]:
    """Extract model/entity definitions from backend code."""
    models = []
    try:
        content = filepath.read_text(errors="replace")
    except IOError:
        return models

    patterns = PYTHON_MODEL_PATTERNS if framework in ("django", "fastapi", "flask") else NEST_MODEL_PATTERNS
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            name = match.group(1)
            # Try to extract fields
            fields = []
            # For Django models: field_name = models.FieldType(...)
            if framework == "django":
                block_start = match.end()
                block = content[block_start:block_start + 2000]
                for fm in re.finditer(
                    r"(\w+)\s*=\s*models\.(\w+)\s*\(([^)]*)\)", block
                ):
                    fields.append({
                        "name": fm.group(1),
                        "type": fm.group(2),
                        "args": fm.group(3).strip()[:100],
                    })
            models.append({
                "name": name,
                "source": str(filepath),
                "framework": framework,
                "fields": fields,
            })
    return models
def count_components(files: List[Path]) -> Dict[str, int]:
    """Count components by type."""
    counts: Dict[str, int] = defaultdict(int)
    for f in files:
        if f.suffix in COMPONENT_EXTENSIONS:
            counts["components"] += 1
        elif f.suffix in {".ts", ".js"}:
            counts["modules"] += 1
    return dict(counts)
