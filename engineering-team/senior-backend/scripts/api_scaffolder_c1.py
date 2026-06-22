# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402
from api_scaffolder_p1 import openapi_type_to_ts  # noqa: F401,E501
from api_scaffolder_p2 import generate_zod_schema, to_pascal_case  # noqa: F401,E501


class APIScaffolderMixin1:
    def generate_types(self):
        """Generate TypeScript type definitions."""
        schemas = self.get_schemas()

        lines = [
            '// Auto-generated TypeScript types',
            f'// Generated from: {self.spec_path.name}',
            f'// Date: {datetime.now().isoformat()}',
            '',
        ]

        for name, schema in schemas.items():
            ts_type = openapi_type_to_ts(schema)
            if ts_type.startswith('{'):
                lines.append(f'export interface {name} {ts_type}')
            else:
                lines.append(f'export type {name} = {ts_type};')
            lines.append('')

        # Generate request/response types from operations
        for op in self.get_operations():
            op_name = to_pascal_case(op['operation_id'])

            # Request body type
            req_body = op.get('request_body', {})
            if req_body:
                content = req_body.get('content', {})
                json_content = content.get('application/json', {})
                schema = json_content.get('schema', {})
                if schema and '$ref' not in schema:
                    ts_type = openapi_type_to_ts(schema)
                    lines.append(f'export interface {op_name}Request {ts_type}')
                    lines.append('')

            # Response type (200 response)
            responses = op.get('responses', {})
            success_resp = responses.get('200', responses.get('201', {}))
            if success_resp:
                content = success_resp.get('content', {})
                json_content = content.get('application/json', {})
                schema = json_content.get('schema', {})
                if schema and '$ref' not in schema:
                    ts_type = openapi_type_to_ts(schema)
                    lines.append(f'export interface {op_name}Response {ts_type}')
                    lines.append('')

        types_file = self.output_dir / 'types.ts'
        types_file.write_text('\n'.join(lines))
        self.generated_files.append(str(types_file))
        print(f"  Generated: {types_file}")
    def generate_validators(self):
        """Generate Zod validation schemas."""
        schemas = self.get_schemas()

        lines = [
            "import { z } from 'zod';",
            '',
            '// Auto-generated Zod validation schemas',
            f'// Generated from: {self.spec_path.name}',
            '',
        ]

        for name, schema in schemas.items():
            zod_schema = generate_zod_schema(schema, name)
            lines.append(zod_schema)
            lines.append(f'export type {name} = z.infer<typeof {name}Schema>;')
            lines.append('')

        # Generate validation middleware
        lines.extend([
            '// Validation middleware factory',
            'import { Request, Response, NextFunction } from "express";',
            '',
            'export function validate<T>(schema: z.ZodSchema<T>) {',
            '  return (req: Request, res: Response, next: NextFunction) => {',
            '    const result = schema.safeParse(req.body);',
            '    if (!result.success) {',
            '      return res.status(400).json({',
            '        error: {',
            '          code: "VALIDATION_ERROR",',
            '          message: "Request validation failed",',
            '          details: result.error.errors.map(e => ({',
            '            field: e.path.join("."),',
            '            message: e.message,',
            '          })),',
            '        },',
            '      });',
            '    }',
            '    req.body = result.data;',
            '    next();',
            '  };',
            '}',
        ])

        validators_file = self.output_dir / 'validators.ts'
        validators_file.write_text('\n'.join(lines))
        self.generated_files.append(str(validators_file))
        print(f"  Generated: {validators_file}")
