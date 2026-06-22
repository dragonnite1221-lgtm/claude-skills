# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402


def generate_zod_schema(schema: Dict, name: str) -> str:
    """Generate Zod validation schema from OpenAPI schema."""
    if not schema:
        return f'export const {name}Schema = z.unknown();'

    def schema_to_zod(s: Dict) -> str:
        if '$ref' in s:
            ref_name = s['$ref'].split('/')[-1]
            return f'{ref_name}Schema'

        s_type = s.get('type', 'unknown')

        if s_type == 'string':
            zod = 'z.string()'
            if 'minLength' in s:
                zod += f'.min({s["minLength"]})'
            if 'maxLength' in s:
                zod += f'.max({s["maxLength"]})'
            if 'pattern' in s:
                zod += f'.regex(/{s["pattern"]}/)'
            if s.get('format') == 'email':
                zod += '.email()'
            if s.get('format') == 'uuid':
                zod += '.uuid()'
            if 'enum' in s:
                values = ', '.join(f"'{v}'" for v in s['enum'])
                return f'z.enum([{values}])'
            return zod

        if s_type == 'integer':
            zod = 'z.number().int()'
            if 'minimum' in s:
                zod += f'.min({s["minimum"]})'
            if 'maximum' in s:
                zod += f'.max({s["maximum"]})'
            return zod

        if s_type == 'number':
            zod = 'z.number()'
            if 'minimum' in s:
                zod += f'.min({s["minimum"]})'
            if 'maximum' in s:
                zod += f'.max({s["maximum"]})'
            return zod

        if s_type == 'boolean':
            return 'z.boolean()'

        if s_type == 'array':
            items_zod = schema_to_zod(s.get('items', {}))
            return f'z.array({items_zod})'

        if s_type == 'object':
            properties = s.get('properties', {})
            required = s.get('required', [])
            if not properties:
                return 'z.record(z.unknown())'

            props = []
            for prop_name, prop_schema in properties.items():
                prop_zod = schema_to_zod(prop_schema)
                if prop_name not in required:
                    prop_zod += '.optional()'
                props.append(f'  {prop_name}: {prop_zod},')

            return 'z.object({\n' + '\n'.join(props) + '\n})'

        return 'z.unknown()'

    return f'export const {name}Schema = {schema_to_zod(schema)};'


def to_camel_case(s: str) -> str:
    """Convert string to camelCase."""
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    words = s.split()
    if not words:
        return s
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])


def to_pascal_case(s: str) -> str:
    """Convert string to PascalCase."""
    s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
    return ''.join(w.capitalize() for w in s.split())


def extract_path_params(path: str) -> List[str]:
    """Extract path parameters from OpenAPI path."""
    return re.findall(r'\{(\w+)\}', path)


def openapi_path_to_express(path: str) -> str:
    """Convert OpenAPI path to Express path format."""
    return re.sub(r'\{(\w+)\}', r':\1', path)
