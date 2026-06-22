# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402


class InferenceOptimizerMixin1:
    def _analyze_pytorch(self) -> Dict[str, Any]:
        """Analyze PyTorch model."""
        try:
            import torch

            # Try to load as checkpoint
            checkpoint = torch.load(str(self.model_path), map_location='cpu')

            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'model' in checkpoint:
                    state_dict = checkpoint['model']
                elif 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                else:
                    state_dict = checkpoint
            else:
                # Assume it's the model itself
                if hasattr(checkpoint, 'state_dict'):
                    state_dict = checkpoint.state_dict()
                else:
                    return {'error': 'Could not extract state dict'}

            # Count parameters
            total_params = 0
            layer_info = []
            for name, param in state_dict.items():
                if hasattr(param, 'numel'):
                    param_count = param.numel()
                    total_params += param_count
                    layer_info.append({
                        'name': name,
                        'shape': list(param.shape),
                        'params': param_count,
                        'dtype': str(param.dtype)
                    })

            return {
                'parameters': total_params,
                'layers': layer_info[:20],  # First 20 layers
                'num_layers': len(layer_info),
            }

        except ImportError:
            logger.warning("torch package not installed, skipping detailed analysis")
            return {}
        except Exception as e:
            logger.error(f"Error analyzing PyTorch model: {e}")
            return {'error': str(e)}
    def benchmark(self, input_size: Tuple[int, int] = (640, 640),
                  batch_sizes: List[int] = None,
                  num_iterations: int = 100,
                  warmup: int = 10) -> Dict[str, Any]:
        """Benchmark model inference speed."""
        if batch_sizes is None:
            batch_sizes = [1, 4, 8, 16]

        logger.info(f"Benchmarking model with input size {input_size}")

        results = {
            'input_size': input_size,
            'num_iterations': num_iterations,
            'warmup_iterations': warmup,
            'batch_results': [],
            'device': 'cpu',
        }

        try:
            if self.model_format == 'onnx':
                results.update(self._benchmark_onnx(input_size, batch_sizes,
                                                    num_iterations, warmup))
            elif self.model_format == 'pytorch':
                results.update(self._benchmark_pytorch(input_size, batch_sizes,
                                                       num_iterations, warmup))
            else:
                results['error'] = f"Benchmarking not supported for {self.model_format}"

        except Exception as e:
            results['error'] = str(e)
            logger.error(f"Benchmark failed: {e}")

        self.benchmark_results = results
        return results
