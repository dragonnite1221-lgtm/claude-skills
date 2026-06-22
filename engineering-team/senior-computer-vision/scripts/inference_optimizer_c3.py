# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402


class InferenceOptimizerMixin3:
    def _benchmark_pytorch(self, input_size: Tuple[int, int],
                          batch_sizes: List[int],
                          num_iterations: int, warmup: int) -> Dict[str, Any]:
        """Benchmark PyTorch model."""
        try:
            import torch
            import numpy as np

            # Load model
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            checkpoint = torch.load(str(self.model_path), map_location=device)

            # Handle different checkpoint formats
            if isinstance(checkpoint, dict) and 'model' in checkpoint:
                model = checkpoint['model']
            elif hasattr(checkpoint, 'forward'):
                model = checkpoint
            else:
                return {'error': 'Could not load model for benchmarking'}

            model.to(device)
            model.train(False)

            results = {'device': str(device)}
            batch_results = []

            with torch.no_grad():
                for batch_size in batch_sizes:
                    dummy = torch.randn(batch_size, 3, *input_size, device=device)

                    # Warmup
                    for _ in range(warmup):
                        _ = model(dummy)
                    if device.type == 'cuda':
                        torch.cuda.synchronize()

                    # Benchmark
                    latencies = []
                    for _ in range(num_iterations):
                        if device.type == 'cuda':
                            torch.cuda.synchronize()
                        start = time.perf_counter()
                        _ = model(dummy)
                        if device.type == 'cuda':
                            torch.cuda.synchronize()
                        latencies.append((time.perf_counter() - start) * 1000)

                    batch_result = {
                        'batch_size': batch_size,
                        'mean_latency_ms': statistics.mean(latencies),
                        'std_latency_ms': statistics.stdev(latencies) if len(latencies) > 1 else 0,
                        'min_latency_ms': min(latencies),
                        'max_latency_ms': max(latencies),
                        'throughput_fps': batch_size * 1000 / statistics.mean(latencies),
                    }
                    batch_results.append(batch_result)

                    logger.info(f"Batch {batch_size}: {batch_result['mean_latency_ms']:.2f}ms, "
                               f"{batch_result['throughput_fps']:.1f} FPS")

            results['batch_results'] = batch_results
            return results

        except ImportError:
            return {'error': 'torch not installed'}
        except Exception as e:
            return {'error': str(e)}
    def get_optimization_recommendations(self, target: str = 'gpu') -> List[Dict[str, Any]]:
        """Get optimization recommendations for target platform."""
        recommendations = []

        key = (self.model_format, target)
        if key in OPTIMIZATION_PATHS:
            path = OPTIMIZATION_PATHS[key]
            for step in path:
                rec = {
                    'step': step,
                    'description': self._get_step_description(step),
                    'expected_speedup': self._get_expected_speedup(step),
                    'command': self._get_step_command(step),
                }
                recommendations.append(rec)

        # Add general recommendations
        if self.model_info:
            params = self.model_info.get('parameters', 0)
            if params and params > 50_000_000:
                recommendations.append({
                    'step': 'pruning',
                    'description': f'Model has {params/1e6:.1f}M parameters. '
                                 'Consider structured pruning to reduce size.',
                    'expected_speedup': '1.5-2x',
                })

            file_size = self.model_info.get('file_size_mb', 0)
            if file_size > 100:
                recommendations.append({
                    'step': 'quantization',
                    'description': f'Model size is {file_size:.1f}MB. '
                                 'INT8 quantization can reduce by 75%.',
                    'expected_speedup': '2-4x',
                })

        return recommendations
