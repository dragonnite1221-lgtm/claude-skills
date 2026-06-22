# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from vision_model_trainer_base import *  # noqa: F403,E402


class VisionModelTrainerMixin1:
    def generate_yolo_config(self, arch: str, epochs: int = 100,
                             batch: int = 16, imgsz: int = 640,
                             **kwargs) -> Dict[str, Any]:
        """Generate Ultralytics YOLO training configuration."""
        if arch not in YOLO_ARCHITECTURES:
            available = ', '.join(YOLO_ARCHITECTURES.keys())
            raise ValueError(f"Unknown architecture: {arch}. Available: {available}")

        arch_info = YOLO_ARCHITECTURES[arch]

        config = {
            'model': f'{arch}.pt',
            'data': str(self.data_dir / 'data.yaml'),
            'epochs': epochs,
            'batch': batch,
            'imgsz': imgsz,
            'patience': 50,
            'save': True,
            'save_period': -1,
            'cache': False,
            'device': '0',
            'workers': 8,
            'project': 'runs/detect',
            'name': f'{arch}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'exist_ok': False,
            'pretrained': True,
            'optimizer': 'auto',
            'verbose': True,
            'seed': 0,
            'deterministic': True,
            'single_cls': False,
            'rect': False,
            'cos_lr': False,
            'close_mosaic': 10,
            'resume': False,
            'amp': True,
            'fraction': 1.0,
            'profile': False,
            'freeze': None,
            'lr0': 0.01,
            'lrf': 0.01,
            'momentum': 0.937,
            'weight_decay': 0.0005,
            'warmup_epochs': 3.0,
            'warmup_momentum': 0.8,
            'warmup_bias_lr': 0.1,
            'box': 7.5,
            'cls': 0.5,
            'dfl': 1.5,
            'pose': 12.0,
            'kobj': 1.0,
            'label_smoothing': 0.0,
            'nbs': 64,
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 0.0,
            'translate': 0.1,
            'scale': 0.5,
            'shear': 0.0,
            'perspective': 0.0,
            'flipud': 0.0,
            'fliplr': 0.5,
            'bgr': 0.0,
            'mosaic': 1.0,
            'mixup': 0.0,
            'copy_paste': 0.0,
            'auto_augment': 'randaugment',
            'erasing': 0.4,
            'crop_fraction': 1.0,
        }

        # Update with user overrides
        config.update(kwargs)

        # Task-specific settings
        if self.task == 'segmentation':
            config['model'] = f'{arch}-seg.pt'
            config['overlap_mask'] = True
            config['mask_ratio'] = 4

        # Metadata
        config['_metadata'] = {
            'architecture': arch,
            'arch_info': arch_info,
            'task': self.task,
            'framework': 'ultralytics',
            'generated_at': datetime.now().isoformat()
        }

        self.config = config
        return config
