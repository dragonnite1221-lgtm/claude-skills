# ruff: noqa: F403, F405, E501
"""
Vision Model Trainer Configuration Generator

Generates training configuration files for object detection and segmentation models.
Supports Ultralytics YOLO, Detectron2, and MMDetection frameworks.

Usage:
    python vision_model_trainer.py <data_dir> --task detection --arch yolov8m
    python vision_model_trainer.py <data_dir> --framework detectron2 --arch faster_rcnn_R_50_FPN
"""
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


logger = logging.getLogger(__name__)


YOLO_ARCHITECTURES = {
    'yolov8n': {'params': '3.2M', 'gflops': 8.7, 'map': 37.3},
    'yolov8s': {'params': '11.2M', 'gflops': 28.6, 'map': 44.9},
    'yolov8m': {'params': '25.9M', 'gflops': 78.9, 'map': 50.2},
    'yolov8l': {'params': '43.7M', 'gflops': 165.2, 'map': 52.9},
    'yolov8x': {'params': '68.2M', 'gflops': 257.8, 'map': 53.9},
    'yolov5n': {'params': '1.9M', 'gflops': 4.5, 'map': 28.0},
    'yolov5s': {'params': '7.2M', 'gflops': 16.5, 'map': 37.4},
    'yolov5m': {'params': '21.2M', 'gflops': 49.0, 'map': 45.4},
    'yolov5l': {'params': '46.5M', 'gflops': 109.1, 'map': 49.0},
    'yolov5x': {'params': '86.7M', 'gflops': 205.7, 'map': 50.7},
}


DETECTRON2_ARCHITECTURES = {
    'faster_rcnn_R_50_FPN': {'backbone': 'R-50-FPN', 'map': 37.9},
    'faster_rcnn_R_101_FPN': {'backbone': 'R-101-FPN', 'map': 39.4},
    'faster_rcnn_X_101_FPN': {'backbone': 'X-101-FPN', 'map': 41.0},
    'mask_rcnn_R_50_FPN': {'backbone': 'R-50-FPN', 'map': 38.6},
    'mask_rcnn_R_101_FPN': {'backbone': 'R-101-FPN', 'map': 40.0},
    'retinanet_R_50_FPN': {'backbone': 'R-50-FPN', 'map': 36.4},
    'retinanet_R_101_FPN': {'backbone': 'R-101-FPN', 'map': 37.7},
}


MMDETECTION_ARCHITECTURES = {
    'faster_rcnn_r50_fpn': {'backbone': 'ResNet50', 'map': 37.4},
    'faster_rcnn_r101_fpn': {'backbone': 'ResNet101', 'map': 39.4},
    'mask_rcnn_r50_fpn': {'backbone': 'ResNet50', 'map': 38.2},
    'yolox_s': {'backbone': 'CSPDarknet', 'map': 40.5},
    'yolox_m': {'backbone': 'CSPDarknet', 'map': 46.9},
    'yolox_l': {'backbone': 'CSPDarknet', 'map': 49.7},
    'detr_r50': {'backbone': 'ResNet50', 'map': 42.0},
    'dino_r50': {'backbone': 'ResNet50', 'map': 49.0},
}


# fmt: off
__all__ = ['Any', 'DETECTRON2_ARCHITECTURES', 'Dict', 'List', 'MMDETECTION_ARCHITECTURES', 'Optional', 'Path', 'YOLO_ARCHITECTURES', 'argparse', 'datetime', 'json', 'logger', 'logging', 'os', 'sys']  # noqa: E501
# fmt: on
