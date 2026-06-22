# ruff: noqa: F403, F405, E501
"""
Inference Optimizer

Analyzes and benchmarks vision models, and provides optimization recommendations.
Supports PyTorch, ONNX, and TensorRT models.

Usage:
    python inference_optimizer.py model.pt --benchmark
    python inference_optimizer.py model.pt --export onnx --output model.onnx
    python inference_optimizer.py model.onnx --analyze
"""
import os
import sys
import json
import argparse
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import statistics


logger = logging.getLogger(__name__)


MODEL_FORMATS = {
    '.pt': 'pytorch',
    '.pth': 'pytorch',
    '.onnx': 'onnx',
    '.engine': 'tensorrt',
    '.trt': 'tensorrt',
    '.xml': 'openvino',
    '.mlpackage': 'coreml',
    '.mlmodel': 'coreml',
}


OPTIMIZATION_PATHS = {
    ('pytorch', 'gpu'): ['onnx', 'tensorrt_fp16'],
    ('pytorch', 'cpu'): ['onnx', 'onnxruntime'],
    ('pytorch', 'edge'): ['onnx', 'tensorrt_int8'],
    ('pytorch', 'mobile'): ['onnx', 'tflite'],
    ('pytorch', 'apple'): ['coreml'],
    ('pytorch', 'intel'): ['onnx', 'openvino'],
    ('onnx', 'gpu'): ['tensorrt_fp16'],
    ('onnx', 'cpu'): ['onnxruntime'],
}


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'MODEL_FORMATS', 'OPTIMIZATION_PATHS', 'Optional', 'Path', 'Tuple', 'argparse', 'datetime', 'json', 'logger', 'logging', 'os', 'statistics', 'sys', 'time']  # noqa: E501
# fmt: on
