# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402


class InferenceOptimizerMixin2:
    def _benchmark_onnx(self, input_size: Tuple[int, int],
                        batch_sizes: List[int],
                        num_iterations: int, warmup: int) -> Dict[str, Any]:
        """Benchmark ONNX model."""
        import numpy as np

        try:
            import onnxruntime as ort

            # Try GPU first, fall back to CPU
            providers = ['CPUExecutionProvider']
            try:
                if 'CUDAExecutionProvider' in ort.get_available_providers():
                    providers = ['CUDAExecutionProvider'] + providers
            except:
                pass

            session = ort.InferenceSession(str(self.model_path), providers=providers)
            input_name = session.get_inputs()[0].name
            device = 'cuda' if 'CUDA' in session.get_providers()[0] else 'cpu'

            results = {'device': device, 'provider': session.get_providers()[0]}
            batch_results = []

            for batch_size in batch_sizes:
                # Create dummy input
                dummy = np.random.randn(batch_size, 3, *input_size).astype(np.float32)

                # Warmup
                for _ in range(warmup):
                    session.run(None, {input_name: dummy})

                # Benchmark
                latencies = []
                for _ in range(num_iterations):
                    start = time.perf_counter()
                    session.run(None, {input_name: dummy})
                    latencies.append((time.perf_counter() - start) * 1000)

                batch_result = {
                    'batch_size': batch_size,
                    'mean_latency_ms': statistics.mean(latencies),
                    'std_latency_ms': statistics.stdev(latencies) if len(latencies) > 1 else 0,
                    'min_latency_ms': min(latencies),
                    'max_latency_ms': max(latencies),
                    'p50_latency_ms': sorted(latencies)[len(latencies) // 2],
                    'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)],
                    'p99_latency_ms': sorted(latencies)[int(len(latencies) * 0.99)],
                    'throughput_fps': batch_size * 1000 / statistics.mean(latencies),
                }
                batch_results.append(batch_result)

                logger.info(f"Batch {batch_size}: {batch_result['mean_latency_ms']:.2f}ms, "
                           f"{batch_result['throughput_fps']:.1f} FPS")

            results['batch_results'] = batch_results
            return results

        except ImportError:
            return {'error': 'onnxruntime not installed'}
