# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402


class InferenceOptimizerMixin0:
    """Analyzes and optimizes vision model inference."""
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model_format = self._detect_format()
        self.model_info = {}
        self.benchmark_results = {}
    def _detect_format(self) -> str:
        """Detect model format from file extension."""
        suffix = self.model_path.suffix.lower()
        if suffix in MODEL_FORMATS:
            return MODEL_FORMATS[suffix]
        raise ValueError(f"Unknown model format: {suffix}")
    def analyze_model(self) -> Dict[str, Any]:
        """Analyze model structure and size."""
        logger.info(f"Analyzing model: {self.model_path}")

        analysis = {
            'path': str(self.model_path),
            'format': self.model_format,
            'file_size_mb': self.model_path.stat().st_size / 1024 / 1024,
            'parameters': None,
            'layers': [],
            'input_shape': None,
            'output_shape': None,
            'ops_count': None,
        }

        if self.model_format == 'onnx':
            analysis.update(self._analyze_onnx())
        elif self.model_format == 'pytorch':
            analysis.update(self._analyze_pytorch())

        self.model_info = analysis
        return analysis
    def _analyze_onnx(self) -> Dict[str, Any]:
        """Analyze ONNX model."""
        try:
            import onnx
            model = onnx.load(str(self.model_path))
            onnx.checker.check_model(model)

            # Count parameters
            total_params = 0
            for initializer in model.graph.initializer:
                param_count = 1
                for dim in initializer.dims:
                    param_count *= dim
                total_params += param_count

            # Get input/output shapes
            inputs = []
            for inp in model.graph.input:
                shape = [d.dim_value if d.dim_value else -1
                        for d in inp.type.tensor_type.shape.dim]
                inputs.append({'name': inp.name, 'shape': shape})

            outputs = []
            for out in model.graph.output:
                shape = [d.dim_value if d.dim_value else -1
                        for d in out.type.tensor_type.shape.dim]
                outputs.append({'name': out.name, 'shape': shape})

            # Count operators
            op_counts = {}
            for node in model.graph.node:
                op_type = node.op_type
                op_counts[op_type] = op_counts.get(op_type, 0) + 1

            return {
                'parameters': total_params,
                'inputs': inputs,
                'outputs': outputs,
                'operator_counts': op_counts,
                'num_nodes': len(model.graph.node),
                'opset_version': model.opset_import[0].version if model.opset_import else None,
            }

        except ImportError:
            logger.warning("onnx package not installed, skipping detailed analysis")
            return {}
        except Exception as e:
            logger.error(f"Error analyzing ONNX model: {e}")
            return {'error': str(e)}
