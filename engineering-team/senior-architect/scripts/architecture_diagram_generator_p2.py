# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from architecture_diagram_generator_base import *  # noqa: F403,E402


class DiagramGenerator:
    """Base class for diagram generators."""

    def __init__(self, scan_result: Dict):
        self.components = scan_result['components']
        self.relationships = scan_result['relationships']
        self.layers = scan_result['layers']
        self.technologies = scan_result['technologies']
        self.external_deps = scan_result['external_deps']

    def generate(self, diagram_type: str) -> str:
        """Generate diagram based on type."""
        if diagram_type == 'component':
            return self._generate_component_diagram()
        elif diagram_type == 'layer':
            return self._generate_layer_diagram()
        elif diagram_type == 'deployment':
            return self._generate_deployment_diagram()
        else:
            return self._generate_component_diagram()

    def _generate_component_diagram(self) -> str:
        raise NotImplementedError

    def _generate_layer_diagram(self) -> str:
        raise NotImplementedError

    def _generate_deployment_diagram(self) -> str:
        raise NotImplementedError
