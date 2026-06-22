# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_diagram_generator_base import *  # noqa: F403,E402
# fmt: off
from architecture_diagram_generator_p2 import DiagramGenerator  # noqa: E402,E501
# fmt: on


class PlantUMLGenerator(DiagramGenerator):
    """Generate PlantUML diagrams."""

    def _generate_component_diagram(self) -> str:
        lines = ['@startuml', 'skinparam componentStyle rectangle', '']

        # Add components
        for name, info in self.components.items():
            file_count = info.get('files', 0)
            lines.append(f'component "{name}\\n({file_count} files)" as {self._safe_id(name)}')

        lines.append('')

        # Add relationships
        seen = set()
        for src, dst, rel_type in self.relationships:
            key = (src, dst)
            if key not in seen:
                seen.add(key)
                lines.append(f'{self._safe_id(src)} --> {self._safe_id(dst)}')

        # External dependencies
        if self.external_deps:
            lines.append('')
            lines.append('package "External Dependencies" {')
            for dep in list(self.external_deps)[:5]:
                lines.append(f'  [{dep}]')
            lines.append('}')

        lines.append('')
        lines.append('@enduml')
        return '\n'.join(lines)

    def _generate_layer_diagram(self) -> str:
        lines = ['@startuml', 'skinparam packageStyle rectangle', '']

        layer_order = ['presentation', 'api', 'business', 'data', 'infrastructure', 'other']

        for layer in layer_order:
            components = self.layers.get(layer, [])
            if components:
                lines.append(f'package "{layer.title()} Layer" {{')
                for comp in components:
                    lines.append(f'  [{comp}]')
                lines.append('}')
                lines.append('')

        lines.append('@enduml')
        return '\n'.join(lines)

    def _generate_deployment_diagram(self) -> str:
        lines = ['@startuml', '']

        lines.append('node "Client" {')
        lines.append('  [Browser/Mobile] as browser')
        lines.append('}')
        lines.append('')

        has_docker = 'docker' in self.technologies
        has_k8s = 'kubernetes' in self.technologies

        lines.append('node "Application Server" {')
        if has_k8s:
            lines.append('  [Kubernetes Cluster] as app')
        elif has_docker:
            lines.append('  [Docker Container] as app')
        else:
            lines.append('  [Application] as app')
        lines.append('}')
        lines.append('')

        lines.append('database "Data Store" {')
        lines.append('  [Database] as db')
        lines.append('}')
        lines.append('')

        lines.append('browser --> app')
        lines.append('app --> db')
        lines.append('')
        lines.append('@enduml')
        return '\n'.join(lines)

    def _safe_id(self, name: str) -> str:
        """Convert name to safe PlantUML ID."""
        return re.sub(r'[^a-zA-Z0-9]', '_', name)
