# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_diagram_generator_base import *  # noqa: F403,E402
# fmt: off
from architecture_diagram_generator_p2 import DiagramGenerator  # noqa: E402,E501
# fmt: on


class MermaidGenerator(DiagramGenerator):
    """Generate Mermaid diagrams."""

    def _generate_component_diagram(self) -> str:
        lines = ['graph TD']

        # Add components
        for name, info in self.components.items():
            safe_name = self._safe_id(name)
            file_count = info.get('files', 0)
            lines.append(f'    {safe_name}["{name}<br/>{file_count} files"]')

        # Add relationships
        seen = set()
        for src, dst, rel_type in self.relationships:
            key = (src, dst)
            if key not in seen:
                seen.add(key)
                lines.append(f'    {self._safe_id(src)} --> {self._safe_id(dst)}')

        # Add external dependencies if any
        if self.external_deps:
            lines.append('')
            lines.append('    subgraph External')
            for dep in list(self.external_deps)[:5]:
                safe_dep = self._safe_id(dep)
                lines.append(f'        {safe_dep}(("{dep}"))')
            lines.append('    end')

        return '\n'.join(lines)

    def _generate_layer_diagram(self) -> str:
        lines = ['graph TB']

        layer_order = ['presentation', 'api', 'business', 'data', 'infrastructure', 'other']

        for layer in layer_order:
            components = self.layers.get(layer, [])
            if components:
                lines.append(f'    subgraph {layer.title()} Layer')
                for comp in components:
                    safe_comp = self._safe_id(comp)
                    lines.append(f'        {safe_comp}["{comp}"]')
                lines.append('    end')
                lines.append('')

        # Add layer relationships (top-down)
        prev_layer = None
        for layer in layer_order:
            if self.layers.get(layer):
                if prev_layer and self.layers.get(prev_layer):
                    first_prev = self._safe_id(self.layers[prev_layer][0])
                    first_curr = self._safe_id(self.layers[layer][0])
                    lines.append(f'    {first_prev} -.-> {first_curr}')
                prev_layer = layer

        return '\n'.join(lines)

    def _generate_deployment_diagram(self) -> str:
        lines = ['graph LR']

        # Client
        lines.append('    subgraph Client')
        lines.append('        browser["Browser/Mobile"]')
        lines.append('    end')
        lines.append('')

        # Determine if we have typical deployment components
        has_api = any('api' in t for t in self.technologies)
        has_docker = 'docker' in self.technologies
        has_k8s = 'kubernetes' in self.technologies

        # Application tier
        lines.append('    subgraph Application')
        if has_k8s:
            lines.append('        k8s["Kubernetes Cluster"]')
        elif has_docker:
            lines.append('        docker["Docker Container"]')
        else:
            lines.append('        app["Application Server"]')
        lines.append('    end')
        lines.append('')

        # Data tier
        lines.append('    subgraph Data')
        lines.append('        db[("Database")]')
        if self.external_deps:
            lines.append('        cache[("Cache")]')
        lines.append('    end')
        lines.append('')

        # Connections
        if has_k8s:
            lines.append('    browser --> k8s')
            lines.append('    k8s --> db')
        elif has_docker:
            lines.append('    browser --> docker')
            lines.append('    docker --> db')
        else:
            lines.append('    browser --> app')
            lines.append('    app --> db')

        return '\n'.join(lines)

    def _safe_id(self, name: str) -> str:
        """Convert name to safe Mermaid ID."""
        return re.sub(r'[^a-zA-Z0-9]', '_', name)
