# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402


def openapi_type_to_ts(schema: Dict) -> str:
    """Convert OpenAPI schema type to TypeScript type."""
    if not schema:
        return 'unknown'

    if '$ref' in schema:
        ref = schema['$ref']
        return ref.split('/')[-1]

    type_map = {
        'string': 'string',
        'integer': 'number',
        'number': 'number',
        'boolean': 'boolean',
        'object': 'Record<string, unknown>',
        'array': 'unknown[]',
    }

    schema_type = schema.get('type', 'unknown')

    if schema_type == 'array':
        items = schema.get('items', {})
        item_type = openapi_type_to_ts(items)
        return f'{item_type}[]'

    if schema_type == 'object':
        properties = schema.get('properties', {})
        if properties:
            props = []
            required = schema.get('required', [])
            for name, prop in properties.items():
                ts_type = openapi_type_to_ts(prop)
                optional = '?' if name not in required else ''
                props.append(f'  {name}{optional}: {ts_type};')
            return '{\n' + '\n'.join(props) + '\n}'
        return 'Record<string, unknown>'

    if 'enum' in schema:
        values = ' | '.join(f"'{v}'" for v in schema['enum'])
        return values

    return type_map.get(schema_type, 'unknown')
