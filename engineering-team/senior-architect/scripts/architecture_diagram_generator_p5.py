# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_diagram_generator_base import *  # noqa: F403,E402
# fmt: off
from architecture_diagram_generator_p2 import DiagramGenerator  # noqa: E402,E501
# fmt: on


class ASCIIGenerator(DiagramGenerator):
    """Generate ASCII diagrams."""

    def _generate_component_diagram(self) -> str:
        lines = []
        lines.append('=' * 60)
        lines.append('COMPONENT DIAGRAM')
        lines.append('=' * 60)
        lines.append('')

        # Components
        lines.append('Components:')
        lines.append('-' * 40)
        for name, info in self.components.items():
            file_count = info.get('files', 0)
            comp_type = info.get('type', 'unknown')
            lines.append(f'  [{name}]')
            lines.append(f'      Files: {file_count}')
            lines.append(f'      Type: {comp_type}')
            lines.append('')

        # Relationships
        if self.relationships:
            lines.append('Relationships:')
            lines.append('-' * 40)
            seen = set()
            for src, dst, rel_type in self.relationships:
                key = (src, dst)
                if key not in seen:
                    seen.add(key)
                    lines.append(f'  {src} --> {dst}')
            lines.append('')

        # External dependencies
        if self.external_deps:
            lines.append('External Dependencies:')
            lines.append('-' * 40)
            for dep in list(self.external_deps)[:10]:
                lines.append(f'  - {dep}')

        lines.append('')
        lines.append('=' * 60)
        return '\n'.join(lines)

    def _generate_layer_diagram(self) -> str:
        lines = []
        lines.append('=' * 60)
        lines.append('LAYERED ARCHITECTURE')
        lines.append('=' * 60)
        lines.append('')

        layer_order = ['presentation', 'api', 'business', 'data', 'infrastructure', 'other']

        for layer in layer_order:
            components = self.layers.get(layer, [])
            if components:
                lines.append(f'+{"-" * 56}+')
                lines.append(f'| {layer.upper():^54} |')
                lines.append(f'+{"-" * 56}+')
                for comp in components:
                    lines.append(f'|   [{comp:^48}]   |')
                lines.append(f'+{"-" * 56}+')
                lines.append('           |')
                lines.append('           v')

        # Remove last arrow
        if lines[-2:] == ['           |', '           v']:
            lines = lines[:-2]

        lines.append('')
        lines.append('=' * 60)
        return '\n'.join(lines)

    def _generate_deployment_diagram(self) -> str:
        lines = []
        lines.append('=' * 60)
        lines.append('DEPLOYMENT DIAGRAM')
        lines.append('=' * 60)
        lines.append('')

        has_docker = 'docker' in self.technologies
        has_k8s = 'kubernetes' in self.technologies

        # Client tier
        lines.append('+----------------------+')
        lines.append('|       CLIENT         |')
        lines.append('|  [Browser/Mobile]    |')
        lines.append('+----------+-----------+')
        lines.append('           |')
        lines.append('           v')

        # Application tier
        lines.append('+----------------------+')
        lines.append('|     APPLICATION      |')
        if has_k8s:
            lines.append('| [Kubernetes Cluster] |')
        elif has_docker:
            lines.append('| [Docker Container]   |')
        else:
            lines.append('| [App Server]         |')
        lines.append('+----------+-----------+')
        lines.append('           |')
        lines.append('           v')

        # Data tier
        lines.append('+----------------------+')
        lines.append('|        DATA          |')
        lines.append('|     [(Database)]     |')
        lines.append('+----------------------+')

        lines.append('')

        # Technologies detected
        if self.technologies:
            lines.append('Technologies detected:')
            lines.append('-' * 40)
            for tech in sorted(self.technologies):
                lines.append(f'  - {tech}')

        lines.append('')
        lines.append('=' * 60)
        return '\n'.join(lines)
