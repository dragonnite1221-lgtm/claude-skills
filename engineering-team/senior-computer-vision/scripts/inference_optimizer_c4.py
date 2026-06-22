# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inference_optimizer_base import *  # noqa: F403,E402


class InferenceOptimizerMixin4:
    def _get_step_description(self, step: str) -> str:
        """Get description for optimization step."""
        descriptions = {
            'onnx': 'Export to ONNX format for framework-agnostic deployment',
            'tensorrt_fp16': 'Convert to TensorRT with FP16 precision for NVIDIA GPUs',
            'tensorrt_int8': 'Convert to TensorRT with INT8 quantization for edge devices',
            'onnxruntime': 'Use ONNX Runtime for optimized CPU/GPU inference',
            'openvino': 'Convert to OpenVINO for Intel CPU/GPU optimization',
            'coreml': 'Convert to CoreML for Apple Silicon acceleration',
            'tflite': 'Convert to TensorFlow Lite for mobile deployment',
        }
        return descriptions.get(step, step)
    def _get_expected_speedup(self, step: str) -> str:
        """Get expected speedup for optimization step."""
        speedups = {
            'onnx': '1-1.5x',
            'tensorrt_fp16': '2-4x',
            'tensorrt_int8': '3-6x',
            'onnxruntime': '1.2-2x',
            'openvino': '1.5-3x',
            'coreml': '2-5x (on Apple Silicon)',
            'tflite': '1-2x',
        }
        return speedups.get(step, 'varies')
    def _get_step_command(self, step: str) -> str:
        """Get command for optimization step."""
        model_name = self.model_path.stem
        commands = {
            'onnx': f'yolo export model={model_name}.pt format=onnx',
            'tensorrt_fp16': f'trtexec --onnx={model_name}.onnx --saveEngine={model_name}.engine --fp16',
            'tensorrt_int8': f'trtexec --onnx={model_name}.onnx --saveEngine={model_name}.engine --int8',
            'onnxruntime': f'pip install onnxruntime-gpu',
            'openvino': f'mo --input_model {model_name}.onnx --output_dir openvino/',
            'coreml': f'yolo export model={model_name}.pt format=coreml',
        }
        return commands.get(step, '')
    def print_summary(self):
        """Print analysis and benchmark summary."""
        print("\n" + "=" * 70)
        print("MODEL ANALYSIS SUMMARY")
        print("=" * 70)

        if self.model_info:
            print(f"Path:        {self.model_info.get('path', 'N/A')}")
            print(f"Format:      {self.model_info.get('format', 'N/A')}")
            print(f"File Size:   {self.model_info.get('file_size_mb', 0):.2f} MB")

            params = self.model_info.get('parameters')
            if params:
                print(f"Parameters:  {params:,} ({params/1e6:.2f}M)")

            if 'num_nodes' in self.model_info:
                print(f"Nodes:       {self.model_info['num_nodes']}")

        if self.benchmark_results and 'batch_results' in self.benchmark_results:
            print("\n" + "-" * 70)
            print("BENCHMARK RESULTS")
            print("-" * 70)
            print(f"Device:      {self.benchmark_results.get('device', 'N/A')}")
            print(f"Input Size:  {self.benchmark_results.get('input_size', 'N/A')}")
            print()
            print(f"{'Batch':<8} {'Latency (ms)':<15} {'Throughput (FPS)':<18} {'P99 (ms)':<12}")
            print("-" * 55)

            for result in self.benchmark_results['batch_results']:
                print(f"{result['batch_size']:<8} "
                      f"{result['mean_latency_ms']:<15.2f} "
                      f"{result['throughput_fps']:<18.1f} "
                      f"{result.get('p99_latency_ms', 0):<12.2f}")

        print("=" * 70 + "\n")
