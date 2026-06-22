# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402


def load_yaml_as_json(content: str) -> Dict:
    """Parse YAML content without PyYAML dependency (basic subset)."""
    lines = content.split('\n')
    result = {}
    stack = [(result, -1)]
    current_key = None
    in_array = False
    array_indent = -1

    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            continue

        indent = len(line) - len(stripped)

        # Pop stack until we find the right level
        while len(stack) > 1 and stack[-1][1] >= indent:
            stack.pop()

        current_obj = stack[-1][0]

        if stripped.startswith('- '):
            # Array item
            value = stripped[2:].strip()
            if isinstance(current_obj, list):
                if ':' in value:
                    # Object in array
                    key, val = value.split(':', 1)
                    new_obj = {key.strip(): val.strip().strip('"').strip("'")}
                    current_obj.append(new_obj)
                    stack.append((new_obj, indent))
                else:
                    current_obj.append(value.strip('"').strip("'"))
        elif ':' in stripped:
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value == '':
                # Check next line for array or object
                new_obj = {}
                current_obj[key] = new_obj
                stack.append((new_obj, indent))
            elif value.startswith('[') and value.endswith(']'):
                # Inline array
                items = value[1:-1].split(',')
                current_obj[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
            else:
                # Simple value
                value = value.strip('"').strip("'")
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                current_obj[key] = value

    return result


def load_spec(spec_path: Path) -> Dict:
    """Load OpenAPI spec from YAML or JSON file."""
    content = spec_path.read_text()

    if spec_path.suffix in ['.yaml', '.yml']:
        try:
            import yaml
            return yaml.safe_load(content)
        except ImportError:
            # Fallback to basic YAML parser
            return load_yaml_as_json(content)
    else:
        return json.loads(content)
