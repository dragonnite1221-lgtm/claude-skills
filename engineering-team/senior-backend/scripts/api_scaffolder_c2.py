# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402
from api_scaffolder_p2 import extract_path_params, openapi_path_to_express, to_camel_case  # noqa: F401,E501


class APIScaffolderMixin2:
    def generate_routes(self):
        """Generate route handlers."""
        operations = self.get_operations()

        # Group by tag
        routes_by_tag: Dict[str, List[Dict]] = {}
        for op in operations:
            tag = op['tags'][0] if op['tags'] else 'default'
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append(op)

        # Generate a route file per tag
        for tag, ops in routes_by_tag.items():
            self.generate_route_file(tag, ops)
    def generate_route_file(self, tag: str, operations: List[Dict]):
        """Generate a single route file."""
        tag_name = to_camel_case(tag)

        lines = [
            "import { Router, Request, Response, NextFunction } from 'express';",
            "import { validate } from './validators';",
            "import * as schemas from './validators';",
            '',
            f'const router = Router();',
            '',
        ]

        for op in operations:
            method = op['method']
            path = openapi_path_to_express(op['path'])
            handler_name = to_camel_case(op['operation_id'])
            summary = op.get('summary', '')

            # Check if has request body
            req_body = op.get('request_body', {})
            has_body = bool(req_body.get('content', {}).get('application/json'))

            # Find schema reference
            schema_ref = None
            if has_body:
                content = req_body.get('content', {}).get('application/json', {})
                schema = content.get('schema', {})
                if '$ref' in schema:
                    schema_ref = schema['$ref'].split('/')[-1]

            lines.append(f'/**')
            if summary:
                lines.append(f' * {summary}')
            lines.append(f' * {method.upper()} {op["path"]}')
            lines.append(f' */')

            middleware = ''
            if schema_ref:
                middleware = f'validate(schemas.{schema_ref}Schema), '

            lines.append(f"router.{method}('{path}', {middleware}async (req: Request, res: Response, next: NextFunction) => {{")
            lines.append('  try {')

            # Extract path params
            path_params = extract_path_params(op['path'])
            if path_params:
                lines.append(f"    const {{ {', '.join(path_params)} }} = req.params;")

            lines.append('')
            lines.append(f'    // TODO: Implement {handler_name}')
            lines.append('')

            # Default response based on method
            if method == 'post':
                lines.append("    res.status(201).json({ message: 'Created' });")
            elif method == 'delete':
                lines.append("    res.status(204).send();")
            else:
                lines.append("    res.json({ message: 'OK' });")

            lines.append('  } catch (err) {')
            lines.append('    next(err);')
            lines.append('  }')
            lines.append('});')
            lines.append('')

        lines.append(f'export default router;')

        route_file = self.output_dir / f'{tag_name}.routes.ts'
        route_file.write_text('\n'.join(lines))
        self.generated_files.append(str(route_file))
        print(f"  Generated: {route_file} ({len(operations)} handlers)")
