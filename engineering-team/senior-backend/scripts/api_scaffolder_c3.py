# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402
from api_scaffolder_p2 import to_camel_case  # noqa: F401,E501


class APIScaffolderMixin3:
    def generate_index(self):
        """Generate index file that combines all routes."""
        operations = self.get_operations()

        # Get unique tags
        tags = set()
        for op in operations:
            tag = op['tags'][0] if op['tags'] else 'default'
            tags.add(tag)

        lines = [
            "import { Router } from 'express';",
            '',
        ]

        for tag in sorted(tags):
            tag_name = to_camel_case(tag)
            lines.append(f"import {tag_name}Routes from './{tag_name}.routes';")

        lines.extend([
            '',
            'const router = Router();',
            '',
        ])

        for tag in sorted(tags):
            tag_name = to_camel_case(tag)
            # Use tag as base path
            base_path = '/' + tag.lower().replace(' ', '-')
            lines.append(f"router.use('{base_path}', {tag_name}Routes);")

        lines.extend([
            '',
            'export default router;',
        ])

        index_file = self.output_dir / 'index.ts'
        index_file.write_text('\n'.join(lines))
        self.generated_files.append(str(index_file))
        print(f"  Generated: {index_file}")
